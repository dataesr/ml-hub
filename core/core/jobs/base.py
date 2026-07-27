"""Base job abstraction."""

from typing import Optional, TypeVar, Generic
from pydantic import BaseModel, Field
from core.common.mlflow import MLflowConfig, MLflowRun
from core.common.ovh import OVHConfig
from core.utils.logger import get_logger
from core.utils.secrets import SECRET_ENV_HF

logger = get_logger(__name__)


TArgs = TypeVar("TArgs", bound=BaseModel)


class BaseJob(BaseModel, Generic[TArgs]):

    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)

    args: TArgs
    mlflow: Optional[MLflowConfig] = None
    ovh: Optional[OVHConfig] = None

    def run(self, mlf: MLflowRun):
        """Job run function to overrides"""

    def execute(self):
        with MLflowRun(self.mlflow) as mlf:
            logger.info(f"[job-{self.name}] Start running")
            logger.debug(f"[job-{self.name}] Args = {self.args.model_dump(exclude_defaults=True)}")
            results = self.run(mlf)
            logger.info(f"[job-{self.name}] Run completed")
        return results

    def submit(self, exec: bool = False):
        """Submit via ovhai CLI. Requires ovh config."""
        if self.ovh is None:
            if exec:
                return self.execute()
            else:
                raise ValueError(f"[job-{self.name}] No OVH config found, cannot submit")

        flags = []
        if self.args:
            flags = self.args.model_dump(exclude_defaults=True).items()

        extra_envs = []
        extra_envs.extend(SECRET_ENV_HF)  # TODO: move this
        if self.mlflow:
            extra_envs.extend(self.mlflow.get_envs())
        logger.info(f"[job-{self.name}] Start submitting")
        return self.ovh.submit_job(flags, extra_envs)


