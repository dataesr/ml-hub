from pydantic import BaseModel
from pipelines.registry import register_pipeline_local, PipelineRegistryLocal
from pipelines.interface import PipelineRunnerBase
from pipelines.utils.logger import get_logger

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
class PipelineRunner(PipelineRunnerBase):

    def run(self, config: BaseModel):
        logger.info(f"Starting pipeline {config.pipeline}...")
        logger.debug(f"Args = {config.args}")
        logger.debug(f"Infra = {config.infra}")

        # Execution logic ...
