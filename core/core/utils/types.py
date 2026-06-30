from pydantic import BaseModel
from typing import Optional


class ENV(BaseModel):
    name: str
    value: str
