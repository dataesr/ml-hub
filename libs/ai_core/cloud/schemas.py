from typing import List, Optional
from pydantic import BaseModel, Field
from ai_core.utils.constants import COMPUTE_GPU
from ai_core.utils.types import ENV


class CloudJobCommandArg(BaseModel):
    name: str
    value: Optional[str] = None


class CloudJobInfrastructure(BaseModel):
    # Image
    image: str
    command: List[str] = Field(default_factory=list)

    # Options
    name: Optional[str] = None
    cpu: Optional[int] = None
    gpu: Optional[int] = 1
    flavor: Optional[str] = COMPUTE_GPU
    envs: List[ENV] = Field(default_factory=list)
    volumes: List[str] = Field(default_factory=list)
    labels: List[ENV] = Field(default_factory=list)


class CloudJobInputs(CloudJobInfrastructure):

    # Image command arguments
    command_args: List[CloudJobCommandArg] = Field(default_factory=list)
