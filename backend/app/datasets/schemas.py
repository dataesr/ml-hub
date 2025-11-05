from pydantic import BaseModel


class DatasetConfig(BaseModel):
    name: str

    class Config:
        extra = "allow"
