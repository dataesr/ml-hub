from typing import Dict, Any
from mlflow.entities import Feedback
from mlflow.genai import scorer
from ai_core.utils import formatters
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def flatten(nested: list):
    return [item for sublist in nested if sublist for item in sublist]


@scorer
def scorer_correct_entities(outputs: str, expectations: Dict[str, Any]):
    correct_entities = 0
    score_entities = 0

    try:
        eval = formatters.tsv_to_data(expectations["expected_response"])
        res = formatters.tsv_to_data(outputs)

        eval_entities = [entity.get("entity") for entity in eval]
        res_entities = [entity.get("entity") for entity in res]

        for eval_e in eval_entities:
            found_e = False
            for res_e in res_entities:
                if eval_e in res_e:
                    correct_entities += 1
                    found_e = True
                if found_e:
                    break

        if len(eval_entities) > 0:
            score_entities = correct_entities / len(eval_entities)

    except Exception as error:
        logger.error(f"Error while formatting data ({error})")

    return Feedback(name="score_correct_entities", value=score_entities, rationale="Correct entities over expected entities")


@scorer
def scorer_correct_grant_ids(outputs: str, expectations: Dict[str, Any]):
    correct_grant_ids = 0
    score_grant_ids = 0

    try:
        eval = formatters.tsv_to_data(expectations["expected_response"])
        res = formatters.tsv_to_data(outputs)

        eval_grant_ids = flatten([entity.get("grant_ids") or entity.get("grants_id") for entity in eval])
        res_grant_ids = flatten([entity.get("grant_ids") or entity.get("grants_id") for entity in res])

        for eval_gi in eval_grant_ids:
            if eval_gi in res_grant_ids:
                correct_grant_ids += 1

        if len(eval_grant_ids) > 0:
            score_grant_ids = correct_grant_ids / len(eval_grant_ids)

    except Exception as error:
        logger.error(f"Error while formatting data ({error})")

    return Feedback(
        name="score_correct_grant_ids",
        value=score_grant_ids,
        rationale="Correct grant_ids over expected grant_ids",
        metadata={"outputs_len": str(len(outputs)), "expectations_len": str(len(expectations))},
    )


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


SCORERS_MAPPING = {
    "is_tsv": is_tsv,
    "is_json": is_json,
    "correct_grant_ids": scorer_correct_grant_ids,
    "correct_entities": scorer_correct_entities,
}
