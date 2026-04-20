"""
Entrypoint: dataset-evaluate
Evaluate model completions using MLflow scorers.
"""

from pydantic import BaseModel
from ai_core.datasets.load import load_from_storage
from ai_core.tracking.client import mlflow_set_experiment
from ai_core.tracking.log import mlflow_start, mlflow_end
from ai_core.tracking.scorers import SCORERS_MAPPING
from ai_core.utils.logger import get_logger
from mlflow.genai import Scorer

logger = get_logger(__name__)


def run(args: BaseModel, tracking=None, **kwargs):
    """Evaluate completions from a dataset using MLflow scorers."""
    # Imports inside the function to avoid dependencies at import time
    import mlflow

    logger.info("Starting pipeline dataset-evaluate...")
    logger.debug(f"with args = {args}")

    # Parse scorers from comma-separated string
    scorers_list: list[str] = []
    scorers_fns: list[Scorer] = []
    if hasattr(args, "scorers") and args.scorers:
        if isinstance(args.scorers, str):
            scorers_list = [s.strip() for s in args.scorers.split(",")]
        elif isinstance(args.scorers, list):
            scorers_list = args.scorers
    for scorer in scorers_list:
        scorers_fns.extend(SCORERS_MAPPING[scorer])
    if len(scorers_fns) == 0:
        raise ValueError(f"No scorers provided ({scorers_list=}), aborting...")

    container = getattr(args, "container", "llm-completions")

    df = load_from_storage(
        args.dataset_name,
        container=container,
    ).to_pandas()
    logger.info(f"✅ Dataset loaded: {df.shape[0]} rows")
    df = df.rename(columns={"input": "inputs", "completion": "expectations", "inference": "outputs"})
    df["expectations"] = df["expectations"].apply(lambda x: {"expected_response": x if isinstance(x, str) else ""})
    if "id" in df.columns:
        df["expectations"] = df[["id", "expectations"]].apply(
            lambda row: {**row["expectations"], "doc_id": row["id"]}, axis=1
        )
    logger.info(f"✅ Dataset ready for evaluation: {df.shape[0]} rows")

    # Use tracking config if available
    project_name = "Default"
    active_model = None
    if tracking:
        project_name = tracking.project_name
        active_model = tracking.set_active_model

    mlflow_set_experiment(experiment_name=project_name)
    mlflow_start(args.model_name, "evaluation")
    mlflow.genai.evaluate(df, scorers=scorers_fns, model_id=active_model)
    mlflow_end()

    logger.info("Pipeline completed.")
    return {"status": "success"}
