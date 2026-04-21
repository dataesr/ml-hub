from typing import Any, Literal
from pydantic import BaseModel, Field
from enum import Enum
from mlflow.genai import scorer, Scorer, scorers
from mlflow.entities import Feedback
from ai_core.tracking.scorers.helpers import (
    dict_similarity,
    Similarity,
    fuzzy_similarity,
    exact_similarity,
    greedy_match,
    weighted_score,
)
from ai_core.utils import formatters
from ai_core.utils.logger import get_logger

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

CATEGORIES = ["funders", "projects", "infrastructures", "private_companies"]

# Weight of each field when computing per-entity field accuracy
FUNDER_FIELD_WEIGHTS: dict[str, float] = {
    "canonical_name": 0.30,
    "funder_short": 0.15,
    "country": 0.15,
    "grant_ids": 0.30,
    "programs": 0.10,
}

PROJECT_FIELD_WEIGHTS: dict[str, float] = {
    "name": 0.40,
    "funder": 0.30,
    "grant_id": 0.30,
}

INFRASTRUCTURE_FIELD_WEIGHTS: dict[str, float] = {
    "name": 0.50,
    "type": 0.30,
    "resource_id": 0.20,
}

PERSON_FIELD_WEIGHTS: dict[str, float] = {
    "name": 0.40,
    "role": 0.40,
    "affiliation": 0.20,
}

COMPANY_FIELD_WEIGHTS: dict[str, float] = {
    "name": 0.50,
    "role": 0.50,
}

WEIGHTS_MAPPING = {
    "funders": FUNDER_FIELD_WEIGHTS,
    "projects": PROJECT_FIELD_WEIGHTS,
    "infrastructures": INFRASTRUCTURE_FIELD_WEIGHTS,
    "private_companies": COMPANY_FIELD_WEIGHTS,
}


class ErrorType(str, Enum):
    MISSED_ENTITY = "missed_entity"  # gold entity not predicted
    HALLUCINATED_ENTITY = "hallucinated_entity"  # predicted entity not in gold
    WRONG_CANONICAL = "wrong_canonical"  # funders: canonical_name wrong
    WRONG_COUNTRY = "wrong_country"  # funders: country wrong
    MISSED_GRANT = "missed_grant"  # grant ID present in gold but absent in pred
    EXTRA_GRANT = "extra_grant"  # grant ID in pred but not in gold
    WRONG_PROGRAM = "wrong_program"  # program missed or wrong
    WRONG_ROLE = "wrong_role"  # persons/companies: role wrong
    WRONG_TYPE = "wrong_type"  # infrastructure: type wrong
    WRONG_FIELD = "wrong_field"  # generic field mismatch


class EvalError(BaseModel):
    error_type: ErrorType
    category: str  # e.g. "funders", "projects"
    doc_id: str
    details: str


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


def funders_similarity(pred: dict[str, Any], gold: dict[str, Any]) -> float | None:
    """Returns a match score 0-1 between two funder dicts"""
    return dict_similarity(
        pred,
        gold,
        similarity_mapping={
            "canonical_name": fuzzy_similarity,
            "funder_short": exact_similarity,
            "mention": fuzzy_similarity,
        },
    )


def projects_similarity(pred: dict, gold: dict) -> float | None:
    """Returns a match score 0-1 between two project dicts"""
    return dict_similarity(
        pred,
        gold,
        similarity_mapping={
            "name": fuzzy_similarity,
            "mention": fuzzy_similarity,
        },
    )


def infrastructures_similarity(pred: dict, gold: dict) -> float | None:
    """Returns a match score 0-1 between two infrastructure dicts"""
    return dict_similarity(
        pred,
        gold,
        similarity_mapping={
            "name": fuzzy_similarity,
            "mention": fuzzy_similarity,
        },
    )


def companies_similarity(pred: dict, gold: dict) -> float | None:
    """Returns a match score 0-1 between two private company dicts"""
    return dict_similarity(
        pred,
        gold,
        similarity_mapping={
            "name": fuzzy_similarity,
            "mention": fuzzy_similarity,
        },
    )


SIMILARITY_FUNCTIONS = {
    "funders": funders_similarity,
    "projects": projects_similarity,
    "infrastructures": infrastructures_similarity,
    "private_companies": companies_similarity,
}


# def score_funder_fields(pred: dict, gold: dict) -> dict[str, float]:
#     return {
#         "canonical_name": fuzzy_similarity(pred.get("canonical_name"), gold.get("canonical_name")),
#         "funder_short": exact_similarity(pred.get("funder_short"), gold.get("funder_short")),
#         "country": exact_similarity(pred.get("country"), gold.get("country")),
#         "grant_ids": list_f1_similarity(
#             pred.get("grant_ids", []),
#             gold.get("grant_ids", []),
#             similarity_fn=exact_similarity,
#         ),
#         "programs": list_f1_similarity(
#             pred.get("programs", []),
#             gold.get("programs", []),
#             similarity_fn=fuzzy_similarity,
#             threshold=0.80,
#         ),
#     }


# def score_project_fields(pred: dict, gold: dict) -> dict[str, float]:
#     return {
#         "name": fuzzy_similarity(pred.get("name"), gold.get("name")),
#         "funder": fuzzy_similarity(pred.get("funder"), gold.get("funder")),
#         "grant_id": exact_similarity(pred.get("grant_id"), gold.get("grant_id")),
#     }


# def score_infra_fields(pred: dict, gold: dict) -> dict[str, float]:
#     return {
#         "name": fuzzy_similarity(pred.get("name"), gold.get("name")),
#         "type": exact_similarity(pred.get("type"), gold.get("type")),
#         "resource_id": exact_similarity(pred.get("resource_id"), gold.get("resource_id")),
#     }


# def score_company_fields(pred: dict, gold: dict) -> dict[str, float]:
#     return {
#         "name": fuzzy_similarity(pred.get("name"), gold.get("name")),
#         "role": exact_similarity(pred.get("role"), gold.get("role")),
#     }


# SCORERS_FUNCTIONS = {
#     "funders": score_funder_fields,
#     "projects": score_project_fields,
#     "infrastructures": score_infra_fields,
#     "private_companies": score_company_fields,
# }


# def detect_funder_errors(pred: dict, gold: dict, doc_id: str) -> list[EvalError]:
#     errors = []
#     if fuzzy_similarity(pred.get("canonical_name"), gold.get("canonical_name")) < 0.85:
#         errors.append(
#             EvalError(
#                 error_type=ErrorType.WRONG_CANONICAL,
#                 category="funders",
#                 doc_id=doc_id,
#                 details=f"pred='{pred.get('canonical_name')}' gold='{gold.get('canonical_name')}'",
#             )
#         )
#     if exact_similarity(pred.get("country"), gold.get("country")) < 1.0:
#         errors.append(
#             EvalError(
#                 error_type=ErrorType.WRONG_COUNTRY,
#                 category="funders",
#                 doc_id=doc_id,
#                 details=f"pred='{pred.get('country')}' gold='{gold.get('country')}'",
#             )
#         )

#     pred_grants = set(x.strip().lower() for x in (pred.get("grant_ids") or []))
#     gold_grants = set(x.strip().lower() for x in (gold.get("grant_ids") or []))
#     for g in gold_grants - pred_grants:
#         errors.append(
#             EvalError(error_type=ErrorType.MISSED_GRANT, category="funders", doc_id=doc_id, details=f"missed grant '{g}'")
#         )
#     for g in pred_grants - gold_grants:
#         errors.append(
#             EvalError(error_type=ErrorType.EXTRA_GRANT, category="funders", doc_id=doc_id, details=f"extra grant '{g}'")
#         )

#     programs_f1 = list_f1_similarity(
#         pred.get("programs", []), gold.get("programs", []), similarity_fn=fuzzy_similarity, threshold=0.80
#     )
#     if programs_f1 < 0.85:
#         errors.append(
#             EvalError(
#                 error_type=ErrorType.WRONG_PROGRAM,
#                 category="funders",
#                 doc_id=doc_id,
#                 details=f"pred={pred.get('programs')} gold={gold.get('programs')}",
#             )
#         )
#     return errors


# def detect_infra_errors(pred: dict, gold: dict, doc_id: str) -> list[EvalError]:
#     errors = []
#     if exact_similarity(pred.get("type"), gold.get("type")) < 1.0:
#         errors.append(
#             EvalError(
#                 error_type=ErrorType.WRONG_TYPE,
#                 category="infrastructures",
#                 doc_id=doc_id,
#                 details=f"pred='{pred.get('type')}' gold='{gold.get('type')}'",
#             )
#         )
#     return errors


# def detect_company_errors(pred: dict, gold: dict, doc_id: str) -> list[EvalError]:
#     errors = []
#     if exact_similarity(pred.get("role"), gold.get("role")) < 1.0:
#         errors.append(
#             EvalError(
#                 error_type=ErrorType.WRONG_ROLE,
#                 category="private_companies",
#                 doc_id=doc_id,
#                 details=f"pred='{pred.get('role')}' gold='{gold.get('role')}'",
#             )
#         )
#     return errors


# DETECT_ERRORS_MAPPING = {
#     "funders": detect_funder_errors,
#     "infrastructures": detect_infra_errors,
#     "private_companies": detect_company_errors,
# }


# class CategoryResult(BaseModel):
#     category: str
#     tp: int = 0
#     fp: int = 0
#     fn: int = 0
#     field_scores: list[float] = Field(default_factory=list)
#     errors: list[EvalError] = Field(default_factory=list)

#     def precision(self) -> float:
#         return self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0.0

#     def recall(self) -> float:
#         return self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0.0

#     def f1(self) -> float:
#         if self.tp == 0 and self.fp == 0 and self.fn == 0:
#             return 1.0  # both empty = correct
#         p = self.precision()
#         r = self.recall()
#         return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

#     def avg_field_accuracy(self) -> float:
#         return sum(self.field_scores) / len(self.field_scores) if self.field_scores else 0.0


# def eval_category(
#     cat: str,
#     pred_items: list[dict[str, Any]],
#     gold_items: list[dict[str, Any]],
#     doc_id: str,
# ) -> CategoryResult:
#     result = CategoryResult(category=cat)
#     sim_fn = SIMILARITY_FUNCTIONS[cat]
#     field_scorer = SCORERS_FUNCTIONS[cat]
#     weights = WEIGHTS_MAPPING[cat]

#     matched, unmatched_preds, unmatched_golds = greedy_match(pred_items, gold_items, sim_fn)

#     result.tp = len(matched)
#     result.fp = len(unmatched_preds)
#     result.fn = len(unmatched_golds)

#     for pred, gold in matched:
#         fs = field_scorer(pred, gold)
#         result.field_scores.append(weighted_score(fs, weights))

#         # Detailed error detection
#         if cat in DETECT_ERRORS_MAPPING:
#             result.errors.extend(detect_funder_errors(pred, gold, doc_id))

#     for g in unmatched_golds:
#         label = g.get("canonical_name") or g.get("name") or g.get("mention") or "?"
#         result.errors.append(
#             EvalError(error_type=ErrorType.MISSED_ENTITY, category=cat, doc_id=doc_id, details=f"missed: '{label}'")
#         )
#     for p in unmatched_preds:
#         label = p.get("canonical_name") or p.get("name") or p.get("mention") or "?"
#         result.errors.append(
#             EvalError(
#                 error_type=ErrorType.HALLUCINATED_ENTITY, category=cat, doc_id=doc_id, details=f"hallucinated: '{label}'"
#             )
#         )

#     return result


# def eval_document(pred: dict[str, Any], gold: dict[str, Any], doc_id: str) -> dict[str, CategoryResult]:
#     results = {}
#     for cat in ["funders", "projects", "infrastructures", "private_companies"]:
#         pred_items = pred.get(cat) or []
#         gold_items = gold.get(cat) or []
#         results[cat] = eval_category(cat, pred_items, gold_items, doc_id)

#     return results


# def eval_grant_ids(pred: dict[str, Any], gold: dict[str, Any]) -> Similarity:
#     pred_funders = pred.get("funders") or []
#     gold_funders = gold.get("funders") or []


#     for gold_funder in gold_funders:


#     similarity = Similarity(preds=pred_grant_ids, golds=gold_grant_ids)
#     return similarity


def eval_funders(pred: dict[str, Any], gold: dict[str, Any]) -> Similarity:
    pred_funders = pred.get("funders") or []
    gold_funders = gold.get("funders") or []

    return Similarity(pred_funders, gold_funders, similarity_fn=funders_similarity)


def eval_document(pred: dict[str, Any], gold: dict[str, Any]) -> dict[str, Any]:
    results = {}

    # funders
    results["funders"] = eval_funders(pred, gold)
    # results["grant_ids"] = eval_grant_ids(pred, gold)
    # results["programs"] = eval_programs(pred, gold)

    # # infrastructures
    # results["infrastructures"] = eval_infra(pred, gold)

    # # private companies
    # results["private_companies"] = eval_companies(pred, gold)

    return results


def eval_row(outputs: str, expectations: dict[str, Any]) -> dict[str, Similarity]:
    pred = _format_data(outputs, format="json")
    gold = _format_data(expectations["expected_response"], format="json")
    if pred is None or gold is None:
        logger.error("Failed to parse outputs or expectations (empty)")
        return {}
    return eval_document(pred, gold)


# class CorpusResult(BaseModel):
#     per_category: dict[str, CategoryResult] = Field(default_factory=dict)
#     all_errors: list[EvalError] = Field(default_factory=list)

#     def macro_f1(self) -> float:
#         # Only include categories that have at least one entity in gold or pred
#         f1s = [r.f1 for r in self.per_category.values() if (r.tp + r.fp + r.fn) > 0]
#         return sum(f1s) / len(f1s) if f1s else 1.0

#     def micro_f1(self) -> float:
#         tp = sum(r.tp for r in self.per_category.values())
#         fp = sum(r.fp for r in self.per_category.values())
#         fn = sum(r.fn for r in self.per_category.values())
#         p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
#         r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
#         return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

#     def error_summary(self) -> dict[str, int]:
#         counts: dict[str, int] = {}
#         for e in self.all_errors:
#             counts[e.error_type.value] += 1
#         return dict(sorted(counts.items(), key=lambda x: -x[1]))


# def eval_aggregate(doc_results: list[dict[str, CategoryResult]]) -> CorpusResult:
#     corpus = CorpusResult()
#     # Accumulate per-category
#     accum: dict[str, CategoryResult] = {cat: CategoryResult(category=cat) for cat in CATEGORIES}

#     for doc in doc_results:
#         for cat, res in doc.items():
#             accum[cat].tp += res.tp
#             accum[cat].fp += res.fp
#             accum[cat].fn += res.fn
#             accum[cat].field_scores.extend(res.field_scores)
#             corpus.all_errors.extend(res.errors)

#     corpus.per_category = accum
#     return corpus


# def trace_attributes(
#     doc_id: str,
#     results: dict[str, CategoryResult],
# ) -> dict[str, Any]:
#     """
#     Flat dict of span attributes for one document trace.
#     MLflow spans accept str / int / float / bool scalar values only.
#     """
#     attrs: dict[str, Any] = {"doc_id": doc_id}

#     for cat in CATEGORIES:
#         r = results[cat]
#         attrs[f"{cat}.precision"] = round(r.precision, 4)
#         attrs[f"{cat}.recall"] = round(r.recall, 4)
#         attrs[f"{cat}.f1"] = round(r.f1, 4)
#         attrs[f"{cat}.field_acc"] = round(r.avg_field_accuracy, 4)
#         attrs[f"{cat}.tp"] = r.tp
#         attrs[f"{cat}.fp"] = r.fp
#         attrs[f"{cat}.fn"] = r.fn

#     all_errors: list[EvalError] = [e for r in results.values() for e in r.errors]
#     for e in all_errors:
#         key = f"error.{e.error_type.value}"
#         attrs[key] = attrs.get(key, 0) + 1

#     # Full error list as JSON string (readable in MLflow trace viewer)
#     attrs["errors_json"] = json.dumps(
#         [{"type": e.error_type.value, "category": e.category, "detail": e.detail} for e in all_errors],
#         ensure_ascii=False,
#     )

#     return attrs


def build_acknowledgement_scorers() -> list[Scorer]:

    @scorer()
    def funders_precision(outputs: str, expectations: dict[str, Any]) -> Feedback:
        similarity = eval_row(outputs, expectations)["funders"]
        precision = similarity.precision()
        if precision is None:
            return Feedback(
                name="funders_precision", value=None, rationale="No funders in gold and pred, precision undefined"
            )
        return Feedback(
            name="funders_precision", value=round(precision, 4), rationale=f"Hallucinated: {similarity.unmatched_preds}"
        )

    @scorer()
    def funders_recall(outputs: str, expectations: dict[str, Any]) -> Feedback:
        similarity = eval_row(outputs, expectations)["funders"]
        recall = similarity.recall()
        if recall is None:
            return Feedback(name="funders_recall", value=None, rationale="No funders in gold and pred, recall undefined")
        return Feedback(name="funders_recall", value=round(recall, 4), rationale=f"Missed: {similarity.unmatched_golds}")

    return [funders_precision, funders_recall]


# def build_acknowledgement_scorers() -> list[Scorer]:
#     scorers: list[Scorer] = []
#     for category in CATEGORIES:

#         @scorer(name=f"{category}_precision")
#         def _precision(outputs: str, expectations: dict[str, Any]) -> float:
#             return round(eval_row(outputs, expectations)[category].precision(), 4)

#         @scorer(name=f"{category}_recall")
#         def _recall(outputs: str, expectations: dict[str, Any]) -> float:
#             return round(eval_row(outputs, expectations)[category].recall(), 4)

#         @scorer(name=f"{category}_f1")
#         def _f1(outputs: str, expectations: dict[str, Any]) -> float:
#             return round(eval_row(outputs, expectations)[category].f1(), 4)

#         @scorer(name=f"{category}_field_accuracy")
#         def _field_accuracy(outputs: str, expectations: dict[str, Any]) -> float:
#             return round(eval_row(outputs, expectations)[category].avg_field_accuracy(), 4)

#         scorers.extend([_precision, _recall, _f1, _field_accuracy])

#     # @scorer(name="micro_f1")
#     # def _micro_f1(outputs: str, expectations: dict[str, Any]) -> float:
#     #     res = eval_row(outputs, expectations)
#     #     tp = sum(r.tp for r in res.values())
#     #     fp = sum(r.fp for r in res.values())
#     #     fn = sum(r.fn for r in res.values())
#     #     p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
#     #     r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
#     #     return round(2 * p * r / (p + r) if (p + r) > 0 else 0.0, 4)

#     @scorer(name="funders_grant_id_recall")
#     def _grant_recall(outputs: str, expectations: dict[str, Any]) -> float:
#         """grant IDs can't be hallucinated from priors."""
#         pred = _format_data(outputs, format="json")
#         gold = _format_data(expectations, format="json")
#         gold_grants = [g for f in (gold.get("funders") or []) for g in (f.get("grant_ids") or [])]
#         pred_grants = [g for f in (pred.get("funders") or []) for g in (f.get("grant_ids") or [])]
#         if not gold_grants:
#             return 1.0
#         hits = sum(1 for g in gold_grants if any(g.strip().lower() == p.strip().lower() for p in pred_grants))
#         return round(hits / len(gold_grants), 4)

#     scorers.extend([_micro_f1, _grant_recall])
#     return scorers


ACKNOWLEDGEMENT_SCORERS = build_acknowledgement_scorers()


# def print_report(corpus: CorpusResult, verbose: bool = False) -> None:
#     SEP = "\n" + "─" * 70 + "\n"
#     report = ""

#     report += f"\n{'ACKNOWLEDGEMENT EXTRACTION — EVAL REPORT':^70}"
#     report += SEP

#     header = f"{'Category':<22} {'P':>6} {'R':>6} {'F1':>6} {'FieldAcc':>9} {'TP':>5} {'FP':>5} {'FN':>5}"
#     report += header
#     report += SEP

#     for cat in CATEGORIES:
#         r = corpus.per_category[cat]
#         report_cat = f"{cat:<22}\n{r.precision:>6.3f}\n{r.recall:>6.3f}\n{r.f1:>6.3f}\n{r.avg_field_accuracy:>9.3f}\n{r.tp:>5}\n{r.fp:>5}\n{r.fn:>5}\n"
#         report += report_cat

#     report += SEP
#     report += f"  Macro F1  : {corpus.macro_f1():.4f}"
#     report += f"\n  Micro F1  : {corpus.micro_f1():.4f}"
#     report += SEP

#     # Error summary
#     report += "\nERROR BREAKDOWN"
#     report += SEP
#     err_summary = corpus.error_summary()
#     total_errors = sum(err_summary.values())
#     for etype, count in err_summary.items():
#         bar = "█" * int(30 * count / max(total_errors, 1))
#         report += f"\n  {etype:<25} {count:>4}  {bar}"
#     report += SEP

#     if verbose and corpus.all_errors:
#         report += "\nDETAILED ERRORS (first 50)"
#         report += SEP
#         for e in corpus.all_errors[:50]:
#             report += f"  [{e.category:<20}] {e.error_type.value:<25} doc={e.doc_id}  {e.detail}\n"
#         if len(corpus.all_errors) > 50:
#             report += f"  ... and {len(corpus.all_errors) - 50} more"
#         report += SEP

#     logger.info(report)


# def build_json_report(corpus: CorpusResult) -> dict:
#     report: dict[str, Any] = {
#         "macro_f1": round(corpus.macro_f1(), 4),
#         "micro_f1": round(corpus.micro_f1(), 4),
#         "per_category": {},
#         "error_breakdown": corpus.error_summary(),
#     }
#     for cat, r in corpus.per_category.items():
#         report["per_category"][cat] = {
#             "precision": round(r.precision, 4),
#             "recall": round(r.recall, 4),
#             "f1": round(r.f1, 4),
#             "avg_field_accuracy": round(r.avg_field_accuracy, 4),
#             "tp": r.tp,
#             "fp": r.fp,
#             "fn": r.fn,
#         }
#     return report
