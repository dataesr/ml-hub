from pydantic import BaseModel
from typing import Literal
from app.experiments.schemas import EXPERIMENTS_PARAMS
from app.types import DICT_PARAMS

JOB_STATE = Literal[
    "QUEUED",
    "PENDING",
    "INITIALIZING",
    "FINALIZING",
    "RUNNING",
    "TIMEOUT",
    "FAILED",
    "ERROR",
    "DONE",
    "INTERRUPTED",
    "INTERRUPTING",
    "SYNC_FAILED",
]

JOB_PIPELINE = Literal["causallm", "causallm-unsloth"]
JOB_DATASET_FORMAT = Literal["auto", "conversational", "text"]
# JOB_MODE = Literal["train", "push"]
JOB_MODE = Literal["train"]


class PROMPTS_PARAMS(BaseModel):
    instruction: str | None = None
    text_format: str | None = None
    chat_template: str | None = None


class JOB_INPUTS(BaseModel):
    model_name: str
    dataset_name: str
    pipeline: JOB_PIPELINE
    experiment_project: str | None = None
    gpu: int | None = None
    dataset_config: str | None = None
    dataset_format: JOB_DATASET_FORMAT | None = None
    mode: JOB_MODE | None = None
    push_model_dir: str | None = None
    hf_hub: str | None = None
    hf_hub_private: bool | None = False
    experiments_params: EXPERIMENTS_PARAMS | None = None
    prompts_params: PROMPTS_PARAMS | None = None
    training_params: DICT_PARAMS | None = None
