from pydantic import BaseModel
from typing import Dict, Any, no_type_check, Optional
from ai_core.pipelines.registry import register_pipeline_cloud, PipelineRegistryCloud
from ai_core.tracking.schemas import TrackingConfig
from ai_core.cloud.schemas import CloudJobInfrastructure, CloudJobVolume
from ai_core.cloud.constants import CONFIGS_CONTAINER, DATASETS_CONTAINER, COMPLETIONS_CONTAINER
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
        image="ghcr.io/ml-hub/cuda-vllm:latest",
        name="dataset-inference",
        volumes=[
            CloudJobVolume(container=CONFIGS_CONTAINER, mount="configs"),
            CloudJobVolume(container=DATASETS_CONTAINER, mount="datasets"),
            CloudJobVolume(container=COMPLETIONS_CONTAINER, mount="completions", permission="RWD"),
        ],
    ),
    tracking=TrackingConfig(),  # default tracking config
)


@no_type_check
@register_pipeline_cloud(pipeline)
def dataset_inference(args: PipelineArgs):
    # Imports should be inside the function to avoid dependencies
    # Make sure selected packages are included in the cloud image
    # import transformers
    # import trl
    # import datasets

    # logger.info(f"Starting pipeline example-cloud...")
    # logger.debug(f"Args = {args}")

    # # Execution logic ...

    # logger.info(f"Pipeline completed.")
    return {"status": "success"}
