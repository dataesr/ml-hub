from typing import Any, Literal

from pydantic import BaseModel

APP_STATE = Literal["QUEUED", "PENDING", "INITIALIZING", "SCALING", "RUNNING", "STOPPING", "STOPPED", "FAILED", "ERROR"]
APP_STATE_STOP = ["STOPPING", "STOPPED", "FAILED", "ERROR"]
APP_STATE_START = ["QUEUED", "PENDING", "INITALIZING", "SCALING", "RUNNING"]
APP_STATE_ERROR = ["FAILED", "ERROR"]

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
