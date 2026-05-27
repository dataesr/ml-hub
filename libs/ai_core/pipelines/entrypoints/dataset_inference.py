"""
Entrypoint: dataset-inference
Run batch inference on a dataset using vLLM.
"""

import os
from typing import no_type_check
from pydantic import BaseModel
from datasets import Dataset
from ai_core.datasets.load import load
from ai_core.datasets.utils import get_prompts, should_use_chat_format
from ai_core.datasets.convert import construct_one_prompt, construct_one_conversation, rename_columns
from ai_core.utils.misc import timestamp
from ai_core.tracking.client import mlflow
from ai_core.tracking.log import (
    mlflow_log_dataset,
    mlflow_start,
    mlflow_end,
    mlflow_active_model,
    mlflow_log_params,
    mlflow_log_artifact,
)
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


@no_type_check
def run(args: BaseModel, **kwargs):
    """Run batch inference on a dataset with vLLM."""
    # GPU imports inside the function to avoid dependencies at import time
    from vllm import LLM, SamplingParams
    from vllm.version import __version__ as VLLM_VERSION

    logger.info("Starting pipeline dataset-inference...")
    logger.debug(f"with args = {args.model_dump(exclude_defaults=True)}")

    ### --- Start tracking ---
    mlflow_start(
        args.model_name,
        run_type="inference",
        tags={"model_name": args.model_name, "dataset_name": args.dataset.path},
    )
    mlflow_active_model()

    ### --- Load dataset ---
    dataset = load(args.dataset_name, split=args.dataset_split)
    mlflow_log_dataset(args.dataset_name, dataset, dataset_split=args.dataset_split)
    logger.info("✅ Dataset loaded")

    sampling_params_dict = getattr(args, "sampling_params", None) or {}
    if sampling_params_dict:
        logger.debug(f"Custom sampling params: {sampling_params_dict}")
    full_params = {
        "seed": 0,
        "temperature": 0,
        "max_tokens": 2048,
        "skip_special_tokens": True,
        **(sampling_params_dict or {}),
    }
    mlflow_log_params(full_params)

    ### --- Load vllm engine ---
    vllm_engine = LLM(
        model=args.model_name,
        quantization="bitsandbytes",
        load_format="bitsandbytes",
        dtype="bfloat16",
        tensor_parallel_size=1,
        trust_remote_code=True,
        enforce_eager=True,
        disable_custom_all_reduce=True,
        disable_log_stats=False,
        max_model_len=12288,
    )
    logger.info(f"✅ vLLM engine {VLLM_VERSION} loaded")

    ### --- Load tokenizer ---
    tokenizer = vllm_engine.get_tokenizer()
    logger.info(f"✅ {args.model_name} tokenizer loaded")

    ### --- Get prompts from dataset ---
    dataset = rename_columns(dataset, input_col=args.dataset.input_column)
    prompts = get_prompts(dataset)
    use_conversation = should_use_chat_format(args.dataset.format, args.dataset.chat_template or tokenizer.chat_template)
    prompts = [
        tokenizer.apply_chat_template(
            construct_one_conversation(
                prompt,
                system=args.dataset.system_prompt,
                tokenize=False,
                add_generation_prompt=True,
            )
            if use_conversation
            else construct_one_prompt(prompt, instruction=args.dataset.system_prompt, text_format=args.dataset.text_format)
        )
        for prompt in prompts
    ]
    logger.info(f"✅ {len(prompts)} prompts formatted")
    logger.debug(f"Example: {prompts[0]}")

    ### --- Generate completions ---
    @mlflow.trace(name="vllm_generate", span_type="llm")
    def vllm_completions():
        outputs = vllm_engine.generate(prompts, SamplingParams(**full_params), use_tqdm=True)
        completions = [output.outputs[0].text for output in outputs]
        logger.debug(f"Generated {len(completions)} completions")
        return completions

    completions = vllm_completions()

    ### --- Merge results ---
    output_col = os.getenv("OUTPUT_COLUMN", "inference")
    if output_col in dataset.column_names:
        logger.warning(f"Existing column '{output_col}' will be overridden by generated completions!")

    # Check completions
    if not isinstance(completions, list):
        raise TypeError(f"Generated completions must be a list, got {type(completions)}")

    if len(completions) != len(dataset):
        logger.error(f"Generated {len(completions)} completions from {len(dataset)} texts, only completions will be saved")
        output = Dataset.from_dict({output_col: completions})
    else:
        logger.info(f"✅ Generated {len(completions)}")
        output = dataset.add_column(output_col, completions)

    ### --- Write results ---
    file_name = f"completions_{timestamp()}.json"
    output_path = f"completions/{file_name}"
    output.to_json(output_path)
    mlflow_log_artifact(output_path, file_name)

    ### --- Finalize ---
    mlflow_end()
    logger.info(f"✅ Inference done! Results saved to {output_path}")
