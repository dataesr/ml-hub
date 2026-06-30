"""
Entrypoint: dataset-evaluate
Evaluate model completions using MLflow scorers.
"""

from core.tracking.schemas import TrackingConfig

from pydantic import BaseModel
import pandas as pd
from core.datasets.load import load_from_storage
from core.tracking.client import mlflow_set_experiment
from core.tracking.log import mlflow_start, mlflow_end, mlflow_log_dict
from core.tracking.scorers import SCORERS_MAPPING
from core.utils.logger import get_logger
import mlflow
from mlflow.genai import Scorer

logger = get_logger(__name__)


def get_scorers_fns(args) -> list[Scorer]:
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
    return scorers_fns


def prepare_inputs(df: pd.DataFrame, args) -> pd.DataFrame:
    input_col = getattr(args, "input_col", "inputs")
    expectation_col = getattr(args, "expectation_col", "completions")
    output_col = getattr(args, "output_col", "outputs")
    id_col = getattr(args, "id_col", "id")
    if input_col not in df.columns or expectation_col not in df.columns or output_col not in df.columns:
        raise ValueError(f"DataFrame must contain columns '{input_col}', '{expectation_col}', and '{output_col}'")
    cols_to_select = [input_col, expectation_col, output_col]
    if id_col in df.columns:
        cols_to_select.append(id_col)
    prep_df = df[cols_to_select].copy()
    prep_df = prep_df.rename(columns={input_col: "inputs", expectation_col: "expectations", output_col: "outputs"})
    prep_df["inputs"] = prep_df["inputs"].apply(lambda x: x if isinstance(x, dict) and "query" in x else {"query": str(x)})
    prep_df["expectations"] = prep_df["expectations"].apply(lambda x: {"expected_response": x})
    prep_df["outputs"] = prep_df["outputs"].apply(lambda x: x.strip() if isinstance(x, str) else x)
    if id_col in df.columns:
        prep_df["inputs"] = prep_df[[id_col, "inputs"]].apply(lambda row: {**row["inputs"], "doc_id": row[id_col]}, axis=1)
    logger.info(f"✅ Dataset ready for evaluation: {prep_df.shape[0]} rows")
    return prep_df


def prepare_output(df: pd.DataFrame) -> pd.DataFrame:
    scores_df = df[["trace_id", "request", "response", "expected_response/value", "assessments"]].copy()
    scores_df["assessments"] = scores_df["assessments"].apply(
        lambda assessments: [
            {
                "name": a.get("assessment_name"),
                "value": a.get("feedback", {}).get("value"),
                "rationale": a.get("rationale"),
                "metadata": {k: v for k, v in a.get("metadata", {}).items() if k not in ["mlflow.assessment.sourceRunId"]},
            }
            for a in assessments
            if a.get("assessment_name") not in ["expected_resposne"]
        ]
    )
    scores_df = scores_df.rename(columns={"expected_response/value": "expected_response", "assessments": "scores"})
    return scores_df.set_index("trace_id", drop=True)


def run(args: BaseModel, tracking: TrackingConfig | None = None, **kwargs):
    """Evaluate completions from a dataset using MLflow scorers."""
    # Imports inside the function to avoid dependencies at import time

    logger.info("Starting pipeline dataset-evaluate...")
    logger.debug(f"with args = {args}")

    # Parse scorers from comma-separated string
    scorers_fns = get_scorers_fns(args)

    # Load and prepare dataset
    container = getattr(args, "container", "llm-completions")
    df = load_from_storage(args.dataset_name, container=container).to_pandas()
    logger.info(f"✅ Dataset loaded: {df.shape[0]} rows")
    df = prepare_inputs(df, args)

    # Use tracking config if available
    project_name = "Default"
    active_model = None
    if tracking:
        project_name = tracking.project_name
        active_model = tracking.set_active_model

    # Run mlflow evaluation
    mlflow_set_experiment(experiment_name=project_name)
    mlflow_start(args.model_name, "evaluation")
    eval_results = mlflow.genai.evaluate(df, scorers=scorers_fns, model_id=active_model)
    scores_df = prepare_output(eval_results.result_df)  # ty:ignore[unresolved-attribute]
    mlflow_log_dict(scores_df.to_dict(orient="index"), f"scores/{eval_results.run_id}.json")
    mlflow_end()

    logger.info("Pipeline completed.")
    return {"status": "success"}
