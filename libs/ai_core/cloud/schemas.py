from typing import List, Optional
from pydantic import BaseModel, Field
from ai_core.cloud.constants import COMPUTE_GPU, VOLUMES_PERMISSIONS, CONTAINERS_REGION
from ai_core.utils.types import ENV


class CloudJobVolume(BaseModel):
    region: str = CONTAINERS_REGION
    container: str
    mount: str
    permission: VOLUMES_PERMISSIONS = "RO"

    def get_link(self):
        return f"{self.container}@{self.region}/:/workspace/{self.mount}:{self.permission}"

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
    volumes: List[CloudJobVolume] = Field(default_factory=list)
    labels: List[ENV] = Field(default_factory=list)


class CloudJobArgument(BaseModel):
    name: str
    value: Optional[str] = None


class CloudJobInputs(CloudJobInfrastructure):

    # Image command arguments
    command_args: List[CloudJobArgument] = Field(default_factory=list)
