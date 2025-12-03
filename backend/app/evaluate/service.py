import pandas as pd
from app.logger import get_logger
from app.datasets import service as datasets_svc
from app.mlflow import mlflow_evaluate
from app.evaluate.helpers import scorers
from app.evaluate.schemas import EVALUATE_INPUTS
from app.logger import get_logger

logger = get_logger(__name__)


# TODO
def get_all():
    return


def get():
    return


def evaluate(eval_inputs: EVALUATE_INPUTS):
    dataset: pd.DataFrame = datasets_svc.load_from_storage(
        eval_inputs.dataset_name,
        container=eval_inputs.container,
        as_pandas=True,
    )
    dataset = dataset.rename(columns={"input": "inputs", "completion": "expectations", "inference": "outputs"})
    dataset["inputs"] = dataset["inputs"].apply(lambda x: {"query": x if isinstance(x, str) else ""})
    dataset["expectations"] = dataset["expectations"].apply(lambda x: {"expected_response": x if isinstance(x, str) else ""})
    mlflow_evaluate(
        dataset,
        scorers=[scorers.is_tsv, scorers.scorer_correct_entities, scorers.scorer_correct_grant_ids],
        experiment_name=eval_inputs.experiment_project,
    )
    return
