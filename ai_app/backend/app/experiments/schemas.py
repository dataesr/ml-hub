from pydantic import BaseModel


class EXPERIMENTS_PARAMS(BaseModel):
    name: str | None = None
    name_tag: str | None = None
    project: str | None = None
    model_id: str | None = None
    disable: bool | None = False
