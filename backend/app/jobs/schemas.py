from pydantic import BaseModel
from typing import Literal

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


class JOB_INPUTS(BaseModel):
    id: str | None = None
    name: str
    gpu: int | None = None
    model_name: str
    dataset_name: str
    dataset_format: Literal["auto", "conversational", "text"] | None = None
    dataset_instruction: str | None = None
    dataset_text_format: str | None = None
    dataset_chat_template: str | None = None
    dataset_volume: bool | None = False
    mode: Literal["train", "push"] | None = None
    push_model_dir: str | None = None
    hf_hub: str | None = None
    hf_hub_private: bool | None = False
    wandb_name: str | None = None
    wandb_project: str | None = None
    wandb_disabled: bool | None = False
