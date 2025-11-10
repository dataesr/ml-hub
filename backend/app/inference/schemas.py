from typing import Any, Literal

from pydantic import BaseModel

APP_STATE = Literal[
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

COMPLETIONS_TASK_STATE = Literal["error", "queued", "running", "done"]
COMPLETIONS_PROMPTS_PARAMS = dict[str, Any]
COMPLETIONS_SAMPLING_PARAMS = dict[str, Any]


class COMPLETIONS_INPUTS(BaseModel):
    inference_url: str = None
    inference_app_id: str = None
    inference_app_start: bool = False
    texts: list[str]
    prompts_params: COMPLETIONS_PROMPTS_PARAMS
    sampling_params: COMPLETIONS_SAMPLING_PARAMS
