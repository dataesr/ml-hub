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


class DatasetConfig(BaseModel):
    """Common dataset configuration shared across jobs."""

    path: str = Field(..., description="HuggingFace dataset name or local path")
    split: str = Field("train", description="Dataset split to use")
    format: Optional[str] = Field(
        None,
        description="Dataset format ('chat' or 'text'). Inferred from structure when not set.",
    )
    text_format: Optional[str] = Field(
        None,
        description="Text prompt template in '{instruction}...{input}...{response}' form.",
    )
    system_prompt: Optional[str] = Field(None, description="System prompt prepended to all inputs")
    chat_template: Optional[str] = Field(None, description="Chat template for conversation formatting")
    instruction_col: str = Field("instruction", description="Column containing the instruction text")
    input_col: str = Field("input", description="Column containing the input text")
    output_col: str = Field("completion", description="Column containing the completion text")
