from pydantic import BaseModel, Field
from typing import Optional, List


class TrackingConfig(BaseModel):
    project_name: str = "Default"
    run_name: Optional[str]
    run_name_tag: Optional[str]
    run_tags: List[str] = Field(default_factory=list)
    set_active_model: Optional[str]
    enable_tracking: bool = True
    enable_log_model: bool = True
    enable_log_dataset: bool = True
