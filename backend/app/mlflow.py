import os
import mlflow
from app.logger import get_logger

logger = get_logger(__name__)


def mlflow_initialize():
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not mlflow_uri:
        logger.warning(f"MLFLOW_TRACKING_URI not set, disable Mlflow monitoring.")
        return

    mlflow.set_tracking_uri(mlflow_uri)
