import os
import mlflow
from typing import Any
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def mlflow_get_client():
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not mlflow_uri:
        logger.warning(f"MLFLOW_TRACKING_URI not set, disable Mlflow monitoring.")
        return

    client = mlflow.MlflowClient(tracking_uri=mlflow_uri)
    return client


def mlflow_initialize():
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not mlflow_uri:
        logger.warning(f"MLFLOW_TRACKING_URI not set, disable Mlflow monitoring.")
        return

    mlflow.set_tracking_uri(mlflow_uri)
    logger.info("Mlflow tracking initialized")


def mlflow_is_enabled():
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
    return mlflow_uri is not None


def mlflow_set_experiment(experiment_id: str | None = None, experiment_name: str | None = None):
    if mlflow_is_enabled():
        mlflow.set_experiment(experiment_id=experiment_id, experiment_name=experiment_name)
