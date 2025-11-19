from pydantic import BaseModel
from typing import Dict, Any

class ENV(BaseModel):
    name: str
    value: str

DICT_PARAMS = Dict[str, Any]
