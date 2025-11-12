from pydantic import BaseModel


class DatasetConfig(BaseModel):
    name: str
    dataset_name: str | None = None
    class Config:
        extra = "allow"
