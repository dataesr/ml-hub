from pydantic import BaseModel
from ai_core.pipelines.registry import register_pipeline_local, PipelineRegistryLocal
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineArgs(BaseModel):
    param_1: str = "example"
    param_2: int = 1


pipeline = PipelineRegistryLocal(
    pipeline="example-local",
    args=PipelineArgs,
    description="Example of a local pipeline",
    tags=["example", "local"],
)


@register_pipeline_local(pipeline)
def example_local_pipeline(args: PipelineArgs):
    # Imports should be inside the function to avoid dependencies
    # Make sure selected packages are installed in the local environment
    import numpy as np
    import pandas as pd

    logger.info("Starting pipeline example-local...")
    logger.debug("Args = {args}")

    # Execution logic ...

    logger.info("Pipeline completed.")
    return {"status": "success"}
