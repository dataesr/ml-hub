from pydantic import BaseModel
from ai_core.pipelines.registry import register_pipeline_local, PipelineRegistryLocal
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineArgs(BaseModel):
    param_1: str
    param_2: int


registry_args = PipelineRegistryLocal(
    pipeline="example-local",
    args=PipelineArgs,
    description="Example of a local pipeline",
    tags=["example", "local"],
)


@register_pipeline_local(registry_args)
def example_local_pipeline(config: BaseModel):
    # Imports should be inside the function to avoid dependencies
    # Make sure selected packages are installed in the local environment
    import numpy as np
    import pandas as pd

    logger.info(f"Starting pipeline {config.pipeline}...")
    logger.debug(f"Args = {config.args}")
    logger.debug(f"Infra = {config.infra}")

    # Execution logic ...

    logger.info(f"Pipeline {config.pipeline} completed.")
    return {"status": "success"}
