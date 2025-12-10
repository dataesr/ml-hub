import os
import mlflow
from typing import Any
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def mlflow_initialize():
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not mlflow_uri:
        logger.warning(f"MLFLOW_TRACKING_URI not set, disable Mlflow monitoring.")
        return

    mlflow.set_tracking_uri(mlflow_uri)
    logger.info("Mlflow tracking initialized")


def mlflow_evaluate(
    data: Any,
    scorers: list,
    model_id: str = None,
    run_name: str = None,
    run_tags: dict = None,
    experiment_name: str = None,
):
    if experiment_name:
        mlflow.set_experiment(experiment_name=experiment_name)
    tags = {"run_type": "evaluation"}
    if run_tags:
        tags.update(tags)
    with mlflow.start_run(run_name=run_name, tags=tags):
        mlflow.genai.evaluate(data=data, scorers=scorers, model_id=model_id)
