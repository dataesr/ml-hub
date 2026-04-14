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

logger = get_logger(__name__)


def run(args: BaseModel, tracking=None, **kwargs):
    """Evaluate completions from a dataset using MLflow scorers."""
    # Imports inside the function to avoid dependencies at import time
    import mlflow

    logger.info("Starting pipeline dataset-evaluate...")
    logger.debug(f"with args = {args}")

    # Parse scorers from comma-separated string
    scorers_list = []
    if hasattr(args, "scorers") and args.scorers:
        if isinstance(args.scorers, str):
            scorers_list = [s.strip() for s in args.scorers.split(",")]
        elif isinstance(args.scorers, list):
            scorers_list = args.scorers

    if not scorers_list:
        raise ValueError("No scorers provided, aborting...")

    container = getattr(args, "container", "llm-completions")

    dataset = load_from_storage(
        args.dataset_name,
        container=container,
    ).to_pandas()
    logger.info(f"✅ Dataset loaded: {len(dataset)} rows")
    dataset = dataset.rename(columns={"input": "inputs", "completion": "expectations", "inference": "outputs"})
    dataset["inputs"] = dataset["inputs"].apply(lambda x: {"query": x if isinstance(x, str) else ""})
    dataset["expectations"] = dataset["expectations"].apply(lambda x: {"expected_response": x if isinstance(x, str) else ""})
    logger.info(f"✅ Dataset renamed: {len(dataset)} rows")

    # Use tracking config if available
    project_name = "Default"
    active_model = None
    if tracking:
        project_name = tracking.project_name or "Default"
        active_model = tracking.set_active_model

    mlflow_set_experiment(experiment_name=project_name)
    mlflow_start(args.model_name, "evaluation")
    mlflow.genai.evaluate(
        dataset,
        scorers=[SCORERS_MAPPING[scorer] for scorer in scorers_list if scorer in SCORERS_MAPPING.keys()],
        model_id=active_model,
    )
    mlflow_end()

    logger.info("Pipeline completed.")
    return {"status": "success"}
