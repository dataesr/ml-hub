from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from ai_core.utils.types import ENV
from ai_core.utils.secrets import SECRET_ENV_MLFLOW

class TrackingConfig(BaseModel):
    project_name: Optional[str] = "Default"
    run_name: Optional[str] = None
    run_name_tag: Optional[str] = None
    set_active_model: Optional[str] = None
    enable_tracking: bool = True
    enable_log_model: bool = True
    enable_log_dataset: bool = True

    def get_envs(self) -> List[ENV]:
        if not self.enable_tracking:
            return []

        base_envs = {
            "MLFLOW_PROJECT_NAME": self.project_name,
            "MLFLOW_RUN_NAME": self.run_name,
            "MLFLOW_RUN_NAME_TAG": self.run_name_tag,
            "MLFLOW_SET_ACTIVE_MODEL": self.set_active_model,
            "MLFLOW_ENABLE_LOG_MODEL": str(self.enable_log_model),
            "MLFLOW_ENABLE_LOG_DATASET": str(self.enable_log_dataset),
        }
        envs = []
        for key, value in base_envs.items():
            if isinstance(value, str) and value not in [None, "", "[]", "{}"]:
                envs.append(ENV(name=key, value=value))
        envs.extend(SECRET_ENV_MLFLOW)
        return envs
