from pydantic import BaseModel, Field
from typing import Optional, List
from ai_core.utils.types import ENV
from ai_core.utils.secrets import SECRET_ENV_MLFLOW

class TrackingConfig(BaseModel):
    project_name: str = "Default"
    run_name: Optional[str] = None
    run_name_tag: Optional[str] = None
    run_tags: List[str] = Field(default_factory=list)
    set_active_model: Optional[str] = None
    enable_tracking: bool = True
    enable_log_model: bool = True
    enable_log_dataset: bool = True

    def get_envs(self) -> List[ENV]:
        if not self.enable_tracking:
            return []
        base_envs = [
            ENV(name="MLFLOW_PROJECT_NAME", value=self.project_name),
            ENV(name="MLFLOW_RUN_NAME", value=self.run_name),
            ENV(name="MLFLOW_RUN_NAME_TAG", value=self.run_name_tag),
            ENV(name="MLFLOW_RUN_TAGS", value=",".join(self.run_tags)),
            ENV(name="MLFLOW_SET_ACTIVE_MODEL", value=self.set_active_model),
            ENV(name="MLFLOW_ENABLE_LOG_MODEL", value=str(self.enable_log_model)),
            ENV(name="MLFLOW_ENABLE_LOG_DATASET", value=str(self.enable_log_dataset)),
        ]
        base_envs.extend(SECRET_ENV_MLFLOW)
        return [env for env in base_envs if env.value not in [None, "", "[]", "{}"]]
