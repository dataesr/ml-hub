from pydantic import BaseModel
from ai_core.pipelines.registry import register_pipeline_cloud, PipelineRegistryCloud
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineArgs(BaseModel):
    learning_rate: float = 2e-5
    epochs: int = 3


registry_args = PipelineRegistryCloud(
    pipeline="example-cloud",
    args=PipelineArgs,
    infrastructure={"image": "ghcr.io/myorg/example-cloud:latest"},
    description="Example of a cloud pipeline",
    tags=["example", "cloud"],
)


@register_pipeline_cloud(registry_args)
def example_cloud_pipeline(config: BaseModel):
    # Imports should be inside the function to avoid dependencies
    # Make sure selected packages are included in the cloud image
    import transformers
    import trl
    import datasets

    logger.info(f"Starting pipeline {self.config.pipeline}...")
    logger.debug(f"Args = {self.config.args}")
    logger.debug(f"Infra = {self.config.infra}")

    # Execution logic ...

    logger.info(f"Pipeline {self.config.pipeline} completed.")
    return {"status": "success"}
