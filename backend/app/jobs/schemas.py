from pydantic import BaseModel
from typing import Any, Literal

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


class JOB_INPUTS(BaseModel):
    model_name: str
    dataset_name: str
    pipeline: JOB_PIPELINE
    name: str | None = None
    gpu: int | None = None
    dataset_format: JOB_DATASET_FORMAT | None = None
    dataset_instruction: str | None = None
    dataset_text_format: str | None = None
    dataset_chat_template: str | None = None
    dataset_volume: bool | None = False
    mode: JOB_MODE | None = None
    push_model_dir: str | None = None
    hf_hub: str | None = None
    hf_hub_private: bool | None = False
    wandb_name: str | None = None
    wandb_project: str | None = None
    wandb_disabled: bool | None = False
    training_args: dict[str, Any] | None = None
