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
    dataset_format: JOB_DATASET_FORMAT | None = None


class JOB_INPUTS(BaseModel):
    name: str | None = None
    gpu: int | None = 1
    experiments_params: EXPERIMENTS_PARAMS | None = None


TRAIN_PIPELINE = Literal["causallm", "causallm-unsloth"]
TRAIN_DATASET_FORMAT = Literal["auto", "conversational", "text"]
# JOB_MODE = Literal["train", "push"]
TRAIN_MODE = Literal["train"]


class TRAIN_INPUTS(JOB_INPUTS):
    model_name: str
    dataset_name: str
    pipeline: TRAIN_PIPELINE
    dataset_config: str | None = None
    dataset_format: TRAIN_DATASET_FORMAT | None = None
    mode: TRAIN_MODE | None = None
    push_model_dir: str | None = None
    hf_push_repo: str | None = None
    experiments_params: EXPERIMENTS_PARAMS | None = None
    prompts_params: PROMPTS_PARAMS | None = None
    training_params: DICT_PARAMS | None = None


class INFERE_INPUTS(JOB_INPUTS):
    model_name: str
    dataset_name: str
    dataset_split: str | None = None
    dataset_config: str | None = None
    prompts_params: PROMPTS_PARAMS | None = None
    sampling_params: DICT_PARAMS | None = None
