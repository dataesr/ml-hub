from typing import Dict, Literal, Union, List
from datasets import Dataset
from pandas import DataFrame
from pydantic import BaseModel
from app.types import DICT_PARAMS

APP_STATE = Literal["QUEUED", "PENDING", "INITIALIZING", "SCALING", "RUNNING", "STOPPING", "STOPPED", "FAILED", "ERROR"]
APP_STATE_STOP = ["STOPPING", "STOPPED", "FAILED", "ERROR"]
APP_STATE_START = ["QUEUED", "PENDING", "INITALIZING", "SCALING", "RUNNING"]
APP_STATE_ERROR = ["FAILED", "ERROR"]

COMPLETIONS_TASK_STATE = Literal["error", "queued", "running", "done"]
COMPLETIONS_PROMPTS_INPUTS = Union[List[str], List[Dict[str, str]], DataFrame, Dataset]

class COMPLETIONS_INPUTS(BaseModel):
    inference_url: str | None = None
    inference_app_id: str | None = None
    inference_app_start: bool | None = False
    inputs: COMPLETIONS_PROMPTS_INPUTS
    inputs_col: str | None = "input"
    prompts_params: DICT_PARAMS | None = None
    sampling_params: DICT_PARAMS | None = None
