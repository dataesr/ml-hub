from mlflow.entities import Feedback
from mlflow.genai import scorer
from ai_core.utils import formatters
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


@scorer
def is_json(outputs: str):
    value = False
    if formatters.json_to_data(outputs):
        value = True
    return Feedback(name="is_json", value=value, rationale="the response is valid json")
    # return value


@scorer
def is_tsv(outputs: str):
    value = False
    if formatters.tsv_to_data(outputs):
        value = True
    return Feedback(name="is_tsv", value=value, rationale="the response is valid tsv")
    # return value


COMMON_SCORERS = {
    "is_json": [is_json],
    "is_tsv": [is_tsv],
}
