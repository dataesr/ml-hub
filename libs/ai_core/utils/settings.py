import os
from ai_core.schemas.types import ENV

SECRET_ENVS: list[ENV] = [
    {"name": "HF_TOKEN", "value": os.getenv("HF_TOKEN")},
    {"name": "MLFLOW_TRACKING_URI", "value": os.getenv("MLFLOW_TRACKING_URI")},
    {"name": "MLFLOW_TRACKING_USERNAME", "value": os.getenv("MLFLOW_TRACKING_USERNAME")},
    {"name": "MLFLOW_TRACKING_PASSWORD", "value": os.getenv("MLFLOW_TRACKING_PASSWORD")},
]
