import os
from ai_core.utils.types import ENV

SECRET_ENV_HF: list[ENV] = [
    {"name": "HF_TOKEN", "value": os.getenv("HF_TOKEN", "")},
]
SECRET_ENV_MLFLOW: list[ENV] = [
    {"name": "MLFLOW_TRACKING_URI", "value": os.getenv("MLFLOW_TRACKING_URI", "")},
    {"name": "MLFLOW_TRACKING_USERNAME", "value": os.getenv("MLFLOW_TRACKING_USERNAME", "")},
    {"name": "MLFLOW_TRACKING_PASSWORD", "value": os.getenv("MLFLOW_TRACKING_PASSWORD", "")},
]
