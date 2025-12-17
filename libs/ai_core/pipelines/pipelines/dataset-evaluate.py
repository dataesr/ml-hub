from typing import List
from pydantic import BaseModel, Field
from ai_core.pipelines.registry import register_pipeline_local, PipelineRegistryLocal
from ai_core.datasets.load import load_from_storage
from ai_core.tracking.client import mlflow_set_experiment
from ai_core.tracking.log import mlflow_start, mlflow_end
from ai_core.tracking.schemas import TrackingConfig
from ai_core.tracking.scorers import SCORERS_MAPPING
from ai_core.cloud.constants import COMPLETIONS_CONTAINER
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineArgs(BaseModel):
    dataset_name: str
    model_name: str = "unnamed"
    container: str = COMPLETIONS_CONTAINER
    scorers: List[str] = Field(default_factory=list)


pipeline = PipelineRegistryLocal(
    pipeline="dataset-evaluate",
    description="Evaluate completions from a dataset or file",
    tags=["dataset", "evaluate"],
    args=PipelineArgs,
    tracking=TrackingConfig(),
)


@register_pipeline_local(pipeline)
def dataset_evaluate(args: PipelineArgs, **kwargs):
    # Imports should be inside the function to avoid dependencies
    # Make sure selected packages are installed in the local environment
    import mlflow

    logger.info("Starting pipeline dataset-evaluate...")
    logger.debug("Args = {args}")

    dataset = load_from_storage(
        args.dataset_name,
        container=args.container,
        as_pandas=True,
    )
    dataset = dataset.rename(columns={"input": "inputs", "completion": "expectations", "inference": "outputs"})
    dataset["inputs"] = dataset["inputs"].apply(lambda x: {"query": x if isinstance(x, str) else ""})
    dataset["expectations"] = dataset["expectations"].apply(lambda x: {"expected_response": x if isinstance(x, str) else ""})

    tracking_dict = kwargs.get("tracking", {})
    tracking = TrackingConfig.model_validate(tracking_dict)

    mlflow_set_experiment(experiment_name=tracking.project_name)
    mlflow_start(args.model_name, "evaluation", tracking.run_tags)
    mlflow.genai.evaluate(
        dataset,
        scorers=[SCORERS_MAPPING[scorer] for scorer in args.scorers if scorer in SCORERS_MAPPING.keys()],
        model_id=tracking.set_active_model,
    )
    mlflow_end()

    logger.info("Pipeline completed.")
    return {"status": "success"}
