from typing import Any
from mlflow.entities import Feedback
from mlflow.genai import scorer
from core.utils import formatters
from core.utils.logger import get_logger

logger = get_logger(__name__)


@scorer
def is_json(outputs: Any):
    value = False
    error_message = ""
    if isinstance(outputs, dict):
        value = True
    if isinstance(outputs, str):
        try:
            formatters.json_to_data(outputs)
            value = True
        except Exception as error:
            error_message = str(error)
    return Feedback(name="is_json", value=value, rationale=error_message or "data is valid json")
    # return value


@scorer
def is_tsv(outputs: str):
    value = False
    error_message = ""
    try:
        formatters.tsv_to_data(outputs)
        value = True
    except Exception as error:
        error_message = str(error)
    return Feedback(name="is_tsv", value=value, rationale=error_message or "data is valid json")
    # return value


COMMON_SCORERS = {
    "is_json": [is_json],
    "is_tsv": [is_tsv],
}
