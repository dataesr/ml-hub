import os
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datasets import Dataset
from ai_core.pipelines.registry import register_pipeline_cloud, PipelineRegistryCloud
from ai_core.tracking.schemas import TrackingConfig
from ai_core.cloud.schemas import CloudJobInfrastructure, CloudJobVolume
from ai_core.cloud.constants import CONFIGS_CONTAINER, DATASETS_CONTAINER, COMPLETIONS_CONTAINER
from ai_core.configs.load import load_prompt_config
from ai_core.datasets.load import load
from ai_core.datasets.utils import get_prompts
from ai_core.utils.misc import timestamp
from ai_core.tracking.client import mlflow
from ai_core.tracking.log import (
    mlflow_log_dataset,
    mlflow_start,
    mlflow_end,
    mlflow_active_model,
    mlflow_log_tags,
    mlflow_log_params,
    mlflow_log_artifact,
)
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineArgs(BaseModel):
    model_name: str
    dataset_name: str
    dataset_split: str = "eval"

    # Config
    prompts_config: Optional[str] = None
    sampling_params: Optional[Dict[str, Any]] = None


pipeline = PipelineRegistryCloud(
    pipeline="dataset-inference",
    description="Inference a dataset with a model",
    tags=["dataset", "inference"],
    args=PipelineArgs,
    infrastructure=CloudJobInfrastructure(
        image="ghcr.io/dataesr/ml-hub/cuda-vllm:latest",
        name="dataset-inference",
        command=["ai-pipeline-run"],
        volumes=[
            CloudJobVolume(container=CONFIGS_CONTAINER, mount="configs"),
            CloudJobVolume(container=DATASETS_CONTAINER, mount="datasets"),
            CloudJobVolume(container=COMPLETIONS_CONTAINER, mount="completions", permission="RWD"),
        ],
    ),
    tracking=TrackingConfig(),  # default tracking config
)

@register_pipeline_cloud(pipeline)
def dataset_inference(args: PipelineArgs):
    # Imports should be inside the function to avoid dependencies
    # Make sure selected packages are included in the cloud image
    from vllm import LLM, SamplingParams
    from vllm.version import __version__ as VLLM_VERSION
    from vllm.transformers_utils.tokenizer import get_tokenizer

    logger.info("Starting pipeline dataset-inference...")
    logger.debug(f"with args = {args.model_dump(exclude_defaults=True)}")

    ### --- Start tracking ---
    mlflow_start(
        args.model_name,
        run_type="inference",
        tags={"model_name": args.model_name, "dataset_name": args.dataset_name},
    )
    mlflow_active_model()

    ### --- Load prompts config ---
    prompts_cfg = None
    if args.prompts_config:
        prompts_cfg = load_prompt_config(args.prompts_config, from_disk=True, disk_folder_path="configs")
        mlflow_log_tags({"prompts_config": args.prompts_config})
        mlflow_log_params(prompts_cfg)

    ### --- Load dataset ---
    dataset = load(args.dataset_name, split=args.dataset_split)
    mlflow_log_dataset(args.dataset_name, dataset, dataset_split=args.dataset_split)
    logger.info("✅ Dataset loaded")

    # Get prompts from dataset
    prompts = get_prompts(dataset)

    if args.sampling_params:
        logger.debug(f"Custom sampling params: {args.sampling_params}")
    full_params = {
        "seed": 0,
        "temperature": 0,
        "max_tokens": 2048,
        "skip_special_tokens": True,
        # "truncate_prompt_tokens": truncate_length,
        **args.sampling_params,
    }
    mlflow_log_params(full_params)

    ### --- Load tokenizer ---
    tokenizer = get_tokenizer(args.model_name, trust_remote_code=True)
    tokenizer.padding_side = "right"
    logger.info(f"✅ {args.model_name} tokenizer loaded")

    ### --- Load vllm engine ---
    vllm_engine = LLM(
        model=args.model_name,
        quantization="bitsandbytes",
        dtype="bfloat16",  # V100 doesnt support bfloat16
        tensor_parallel_size=1,  # torch.cuda.device_count()
        trust_remote_code=True,
        # enforce_eager=True,
        disable_custom_all_reduce=True,
        disable_log_stats=False,
        max_model_len=12288,  # TODO: compute expected max len
    )
    logger.info(f"✅ vLLM engine {VLLM_VERSION} loaded")

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
