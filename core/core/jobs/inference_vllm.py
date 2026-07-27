"""
Run batch inference on a dataset using vLLM.
"""

import mlflow
from pydantic import BaseModel, Field
from datasets import Dataset
from core.common.mlflow import MLflowRun
from core.common.datasets import (
    DatasetConfig,
    load_and_format_dataset,
    OUTPUT_COLUMN,
)
from core.utils.misc import timestamp
from core.utils.logger import get_logger

logger = get_logger(__name__)


class VLLMSamplingParams(BaseModel):
    """vLLM sampling parameters."""

    seed: int = Field(0, description="Random seed")
    temperature: float = Field(0, description="Sampling temperature")
    max_tokens: int = Field(2048, description="Maximum tokens to generate")
    skip_special_tokens: bool = Field(False, description="Skip special tokens in output")


class InferenceVLLMArgs(BaseModel):
    """Arguments for the inference job (vLLM batch inference)."""

    model_name: str = Field(..., description="HuggingFace model name or path")
    dataset: DatasetConfig = Field(..., description="Dataset configuration")
    max_model_len: int = Field(2048, description="vLLM max model length")
    sampling_params: VLLMSamplingParams = Field(default=VLLMSamplingParams())


def run_inference_vllm(
    args: InferenceVLLMArgs,
    mlf: MLflowRun,
    return_output_dataset: bool = False,
    start_tracking: bool = True,
):
    """Run batch inference on a dataset with vLLM."""
    # GPU imports inside the function to avoid dependencies at import time
    from vllm import LLM, SamplingParams  # ty:ignore[unresolved-import]
    from vllm.version import __version__ as VLLM_VERSION  # ty:ignore[unresolved-import]

    ### --- Start tracking ---
    if start_tracking:
        mlf.start_run(f"infer-{args.model_name}", tags={"run_type": "inference-vllm"})
    mlf.set_active_model(model_name=args.model_name)

    sampling_params = args.sampling_params
    if sampling_params.model_dump(exclude_defaults=True):
        logger.debug(f"Custom sampling params: {sampling_params.model_dump(exclude_defaults=True)}")
    mlf.log_params(sampling_params.model_dump())

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

    ### --- Load and format dataset ---
    dataset, use_chat_format = load_and_format_dataset(
        args.dataset,
        dataset_chat_template=tokenizer.chat_template,
    )
    mlf.log_dataset(args.dataset.path, dataset, dataset_split=args.dataset.split)
    logger.info("✅ Dataset loaded")

    prompts = dataset[dataset.column_names[0]]  # Use the first column as prompts
    if use_chat_format:
        prompts = [
            tokenizer.apply_chat_template(
                prompt,
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
        outputs = vllm_engine.generate(prompts, SamplingParams(**sampling_params.model_dump()), use_tqdm=True)
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
    if return_output_dataset:
        return output
    return output_path
