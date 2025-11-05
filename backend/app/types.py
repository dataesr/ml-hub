from pydantic import BaseModel


class ENV(BaseModel):
    name: str
    value: str
