from typing import no_type_check
from pydantic import BaseModel
from ai_core.pipelines.registry import register_pipeline_cloud, PipelineRegistryCloud
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineArgs(BaseModel):
    learning_rate: float = 2e-5
    epochs: int = 3


pipeline = PipelineRegistryCloud(
    pipeline="example-cloud",
    args=PipelineArgs,
    infrastructure={"image": "ghcr.io/myorg/example-cloud:latest", "gpu": 2},
    description="Example of a cloud pipeline",
    tags=["example", "cloud"],
)


@no_type_check
@register_pipeline_cloud(pipeline)
def example_cloud_pipeline(args: PipelineArgs):
    # Imports should be inside the function to avoid dependencies
    # Make sure selected packages are included in the cloud image
    # import transformers
    # import trl
    # import datasets

    logger.info("Starting pipeline example-cloud...")
    logger.debug(f"args = {args.model_dump(exclude_defaults=True)}")

    # Execution logic ...

    logger.info("Pipeline completed.")
    return {"status": "success"}
