from pydantic import BaseModel
from typing import Dict, Any, List, Type, Callable
from ai_core.schemas.constants import COMPUTE_GPU
from ai_core.schemas.types import ENV


class JobInput(BaseModel):
    # Required
    image: str

    # Optional
    name: str | None = None
    cpu: int | None = None
    gpu: int | None = 1
    flavor: str | None = COMPUTE_GPU
    envs: List[ENV] | None = None
    labels: List[ENV] | None = None
    experiments_params: Dict[str, Any] | None = None
    pipeline_config: str | None = None


# class FinetuneInput(BaseInput):
#     # Required
#     model_name: str
#     dataset_name: str

#     # Optional
#     dataset_split: str | None = None
#     hf_push_repo: str | None = None
#     prompt_config: str | None = None


# class InfereInput(BaseInput):
#     # Required
#     model_name: str
#     dataset_name: str

#     # Optional
#     dataset_split: str | None = None
#     prompt_config: str | None = None
#     sampling_params: Dict[str, Any] | None = None
