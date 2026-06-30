from typing import Any, Literal, Callable
from mlflow.genai import Scorer
from mlflow.genai.scorers import scorer
from mlflow.entities import Feedback
from core.tracking.scorers.helpers import (
    Similarity,
    fuzzy_similarity,
    exact_similarity,
    dict_matching,
    field_list_matching,
)
from core.utils import formatters
from core.utils.logger import get_logger

logger = get_logger(__name__)

# SCHEMA
# {
#     "text": "This work was supported by....",
#     "publication_id": "doi10.1101...",
#     "funders": [
#       {
#         "mention": "National Natural Science Foundation of China",
#         "canonical_name": "National Natural Science Foundation of China",
#         "funder_short": "NSFC",
#         "country": "CN",
#         "grant_ids": [
#           "62272023",
#           "51991391",
#           "51991395"
#         ],
#         "programs": ["CIFRE", ...]
#       }
#       ...
#     ],
#     "projects": [
#       {
#         "mention": "National Natural Science Foundation of China (62272023, 51991391, 51991395)",
#         "grant_id": "62272023",
#         "funders": [
#           "National Natural Science Foundation of China", ...
#         ]
#       }
#     ],
#     "infrastructures": [
#       {
#         "mention": "Computational facilities",
#         "name": "Computational facilities",
#         "type": "computational_facility"
#       }
#       ...
#     ],
#     "private_companies": [
#       {
#         "mention": "Huawei Technologies",
#         "name": "Huawei Technologies",
#         "role": "funding"
#       }
#       ...
#     ]
#   },

NA_ENTITIES = Exception("NO ENTITIES")


def _format_data(data: Any, format: Literal["json", "tsv"] = "json") -> dict[str, Any]:
    try:
        formatter_fn = formatters.formatters_func.get(format)
        if formatter_fn is None:
            raise ValueError(f"Unsupported format '{format}'")
        if format == "json" and isinstance(data, dict):
            return data
        return formatter_fn(data)
    except Exception as error:
        raise Exception(f"Error while formatting data as {format}: {error}")


def eval_funders(pred: dict[str, Any], gold: dict[str, Any]) -> Similarity:
    pred_funders = pred.get("funders", [])
    gold_funders = gold.get("funders", [])

    matched, unmatched_preds, unmatched_golds = dict_matching(
        pred_funders,
        gold_funders,
        similarity_mapping={
            "canonical_name": fuzzy_similarity,
            "funder_short": exact_similarity,
            "mention": fuzzy_similarity,
        },
    )

    return Similarity(matched, unmatched_preds, unmatched_golds, pred_funders, gold_funders)


def eval_grant_ids(funders_similarity: Similarity) -> Similarity:
    # Extract grant_ids from matched funders only (requires funder match first, then extract grant_ids for those matched funders)
    golds = [
        (match[1].get("canonical_name"), set(match[1].get("grant_ids", [])))
        for match in funders_similarity.matched
        if match[1].get("grant_ids", [])
    ]
    matched, unmatched_preds, unmatched_golds = field_list_matching(
        funders_similarity.matched,
        field="grant_ids",
        parent_name_field="canonical_name",
    )
    return Similarity(matched, unmatched_preds, unmatched_golds, golds=golds)


def eval_projects(pred: dict[str, Any], gold: dict[str, Any]) -> Similarity:
    pred_projects = pred.get("projects", [])
    gold_projects = gold.get("projects", [])

    matched, unmatched_preds, unmatched_golds = dict_matching(
        pred_projects,
        gold_projects,
        similarity_mapping={
            "name": fuzzy_similarity,
            "mention": fuzzy_similarity,
        },
    )

    return Similarity(matched, unmatched_preds, unmatched_golds, pred_projects, gold_projects)


def eval_infrastructures(pred: dict[str, Any], gold: dict[str, Any]) -> Similarity:
    pred_infra = pred.get("infrastructures", [])
    gold_infra = gold.get("infrastructures", [])

    matched, unmatched_preds, unmatched_golds = dict_matching(
        pred_infra,
        gold_infra,
        similarity_mapping={
            "name": fuzzy_similarity,
            "mention": fuzzy_similarity,
        },
    )

    return Similarity(matched, unmatched_preds, unmatched_golds, pred_infra, gold_infra)


def eval_private_companies(pred: dict[str, Any], gold: dict[str, Any]) -> Similarity:
    pred_companies = pred.get("private_companies", [])
    gold_companies = gold.get("private_companies", [])

    matched, unmatched_preds, unmatched_golds = dict_matching(
        pred_companies,
        gold_companies,
        similarity_mapping={
            "name": fuzzy_similarity,
            "mention": fuzzy_similarity,
        },
    )

    return Similarity(matched, unmatched_preds, unmatched_golds, pred_companies, gold_companies)


def eval_trace(outputs: str, expectations: dict[str, Any]) -> dict[str, Similarity]:
    pred = _format_data(outputs, format="json")
    gold = _format_data(expectations["expected_response"], format="json")
    results = {}

    if pred is None or gold is None:
        logger.error("Failed to parse outputs or expectations (empty)")
        return results

    # funders
    results["funders"] = eval_funders(pred, gold)
    results["grant_ids"] = eval_grant_ids(results["funders"])

    # projects
    results["projects"] = eval_projects(pred, gold)

    # # infrastructures
    results["infrastructures"] = eval_infrastructures(pred, gold)

    # # private companies
    results["private_companies"] = eval_private_companies(pred, gold)

    return results


def entity_scorer(
    entity: str,
    outputs: str,
    expectations: dict[str, Any],
    extract_value: Callable,
    extract_match_value: Callable | None = None,
) -> list[Feedback]:
    feedbacks = []
    if extract_match_value is None:
        extract_match_value = extract_value

    similarity = eval_trace(outputs, expectations)[entity]
    precision = similarity.precision()
    recall = similarity.recall()
    matches = [extract_match_value(matched) for matched in similarity.matched]
    hallucinations = [extract_value(unmatched) for unmatched in similarity.unmatched_preds]
    misses = [extract_value(unmatched) for unmatched in similarity.unmatched_golds]

    feedbacks.append(
        Feedback(
            name=f"{entity}_score",
            value=len(matches) / len(similarity.golds) if similarity.golds else 1.0,
            rationale=f"{len(matches)}/{len(similarity.golds)} correct, {len(hallucinations)} hallucinated, {len(misses)} missed {entity}",
            metadata={"matched": ", ".join(matches)} if matches else {},
        )
    )

    if precision is not None:
        feedbacks.append(
            Feedback(
                name=f"{entity}_precision",
                value=round(precision, 4),
                rationale=f"{len(hallucinations)} hallucinated {entity}",
                metadata={"hallucinations": ", ".join(hallucinations)} if hallucinations else {},
            )
        )

    if recall is not None and similarity.golds:
        feedbacks.append(
            Feedback(
                name=f"{entity}_recall",
                value=round(recall, 4),
                rationale=f"{len(misses)} missed {entity}",
                metadata={"misses": ", ".join(misses)} if misses else {},
            )
        )

    return feedbacks


def build_acknowledgement_scorers() -> list[Scorer]:

    @scorer(name="funders_score")
    def funders_scorer(outputs: str, expectations: dict[str, Any]) -> list[Feedback]:
        return entity_scorer(
            "funders",
            outputs,
            expectations,
            extract_value=lambda x: x.get("canonical_name", x.get("mention", "unknown")),
            extract_match_value=lambda x: x[1].get("canonical_name", x[1].get("mention", "unknown")),  # x[1] = gold
        )

    @scorer(name="grant_ids_score")
    def grant_ids_scorer(outputs: str, expectations: dict[str, Any]) -> list[Feedback]:
        return entity_scorer(
            "grant_ids",
            outputs,
            expectations,
            extract_value=lambda x: f"{x[0]}: {', '.join(list(x[1]))}",  # x is a tuple of (parent_name, set(grant_ids))
        )

    @scorer(name="projects_score")
    def projects_scorer(outputs: str, expectations: dict[str, Any]) -> list[Feedback]:
        return entity_scorer(
            "projects",
            outputs,
            expectations,
            extract_value=lambda x: x.get("name", x.get("mention", "unknown")),
            extract_match_value=lambda x: x[1].get("name", x[1].get("mention", "unknown")),
        )

    @scorer(name="infrastructures_score")
    def infrastructures_scorer(outputs: str, expectations: dict[str, Any]) -> list[Feedback]:
        return entity_scorer(
            "infrastructures",
            outputs,
            expectations,
            extract_value=lambda x: x.get("name", x.get("mention", "unknown")),
            extract_match_value=lambda x: x[1].get("name", x[1].get("mention", "unknown")),
        )

    @scorer(name="private_companies_score")
    def private_companies_scorer(outputs: str, expectations: dict[str, Any]) -> list[Feedback]:
        return entity_scorer(
            "private_companies",
            outputs,
            expectations,
            extract_value=lambda x: x.get("name", x.get("mention", "unknown")),
            extract_match_value=lambda x: x[1].get("name", x[1].get("mention", "unknown")),
        )

    return [
        funders_scorer,
        grant_ids_scorer,
        projects_scorer,
        infrastructures_scorer,
        private_companies_scorer,
    ]


ACKNOWLEDGEMENT_SCORERS = build_acknowledgement_scorers()
