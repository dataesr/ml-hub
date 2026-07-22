"""
Run batch inference on a dataset using Scaleway.
"""

import mlflow
from pydantic import BaseModel, Field
from datasets import Dataset
from core.jobs.base import DatasetConfig, SamplingParamsConfig
from core.common.mlflow import MLflowRun
from core.common.datasets import (
    load,
    get_prompts,
    should_use_chat_format,
    construct_one_prompt,
    construct_one_conversation,
    rename_columns,
    OUTPUT_COLUMN,
)
from core.utils.misc import timestamp
from core.utils.logger import get_logger

logger = get_logger(__name__)


class InferenceSCWArgs(BaseModel):
    """Arguments for the inference job (Scaleway inference)."""

    model_name: str = Field(..., description="HuggingFace model name or path")
    dataset: DatasetConfig = Field(..., description="Dataset configuration")
    max_model_len: int = Field(2048, description="vLLM max model length")
    sampling_params: SamplingParamsConfig = Field(
        default_factory=SamplingParamsConfig,
        description="vLLM sampling parameters",
    )


def run_inference_scw(args: InferenceSCWArgs, mlf: MLflowRun):
    """Run batch inference on a dataset with Scaleway."""
    # GPU imports inside the function to avoid dependencies at import time
    from vllm import LLM, SamplingParams  # ty:ignore[unresolved-import]
    from vllm.version import __version__ as VLLM_VERSION  # ty:ignore[unresolved-import]

    ### --- Start tracking ---
    mlf.start_run(f"infer-{args.model_name}", tags={"run_type": "inference"})
    mlf.set_active_model(model_name=args.model_name)

    ### --- Load dataset ---
    dataset = load(args.dataset.path, split=args.dataset.split)
    mlf.log_dataset(args.dataset.path, dataset, dataset_split=args.dataset.split)
    logger.info("✅ Dataset loaded")

    sampling_params = args.sampling_params
    if sampling_params.model_dump(exclude_defaults=True):
        logger.debug(f"Custom sampling params: {sampling_params.model_dump(exclude_defaults=True)}")
    full_params = {
        "seed": 0,
        "temperature": 0,
        "max_tokens": 2048,
        "skip_special_tokens": True,
        **(sampling_params.model_dump() or {}),
    }
    mlf.log_params(full_params)

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
        max_model_len=args.max_model_len or 2048,
    )
    logger.info(f"✅ vLLM engine {VLLM_VERSION} loaded")

    ### --- Load tokenizer ---
    tokenizer = vllm_engine.get_tokenizer()
    logger.info(f"✅ {args.model_name} tokenizer loaded")

    ### --- Get prompts from dataset ---
    dataset = rename_columns(dataset, input_col=args.dataset.input_col)
    prompts = get_prompts(dataset)
    use_conversation = should_use_chat_format(args.dataset.format, args.dataset.chat_template or tokenizer.chat_template)
    prompts = [
        tokenizer.apply_chat_template(
            (
                construct_one_conversation(
                    prompt,
                    system=args.dataset.system_prompt,
                )
                if use_conversation
                else construct_one_prompt(
                    prompt, instruction=args.dataset.system_prompt, text_format=args.dataset.text_format
                )
            ),
            tokenize=False,
            add_generation_prompt=True,
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
    output_col = args.dataset.output_col or OUTPUT_COLUMN
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
        output: Dataset = dataset.add_column(output_col, completions)

    ### --- Write results ---
    file_name = f"completions_{timestamp()}.json"
    output_path = f"completions/{file_name}"
    output.to_json(output_path)
    mlf.log_artifact(output_path, file_name)

    ### --- Finalize ---
    logger.info(f"✅ Inference done! Results saved to {output_path}")
