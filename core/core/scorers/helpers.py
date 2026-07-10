from rapidfuzz import fuzz
from typing import Any, TypeVar, Callable
from pydantic import BaseModel, Field
from core.utils.logger import get_logger

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.85

T = TypeVar("T")

# class Similarity(BaseModel):
#     preds: list = Field(default_factory=list)
#     golds: list = Field(default_factory=list)
#     matched: list[tuple] = Field(default_factory=list)
#     unmatched_preds: list = Field(default_factory=list)
#     unmatched_golds: list = Field(default_factory=list)
#     tp: int = 0
#     fp: int = 0
#     fn: int = 0

#     def __init__(
#         self,
#         preds: list[T],
#         golds: list[T],
#         matching_fn: Callable[[list[T], list[T]], tuple[list[tuple[T, T]], list[T], list[T]]],
#     ):
#         super().__init__(preds=preds, golds=golds)
#         self.matched, self.unmatched_preds, self.unmatched_golds = matching_fn(preds, golds)
#         self.tp = len(self.matched)
#         self.fp = len(self.unmatched_preds)
#         self.fn = len(self.unmatched_golds)

#     def precision(self) -> float | None:
#         if not self.preds and not self.golds:
#             return None
#         return self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0.0

#     def recall(self) -> float | None:
#         if not self.preds and not self.golds:
#             return None
#         return self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0.0

#     def f1(self) -> float | None:
#         if not self.preds and not self.golds:
#             return None
#         p = self.precision()
#         r = self.recall()
#         if p is None or r is None:
#             return None
#         f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
#         return f1


class Similarity(BaseModel):
    preds: list = Field(default_factory=list)
    golds: list = Field(default_factory=list)
    matched: list[tuple] = Field(default_factory=list)
    unmatched_preds: list = Field(default_factory=list)
    unmatched_golds: list = Field(default_factory=list)
    tp: int = 0
    fp: int = 0
    fn: int = 0

    def __init__(
        self,
        matched: list[tuple[T, T]],
        unmatched_preds: list[T],
        unmatched_golds: list[T],
        preds: list[T] | None = None,
        golds: list[T] | None = None,
    ):
        super().__init__(
            matched=matched,
            unmatched_preds=unmatched_preds,
            unmatched_golds=unmatched_golds,
            preds=preds or [],
            golds=golds or [],
        )
        self.tp = len(self.matched)
        self.fp = len(self.unmatched_preds)
        self.fn = len(self.unmatched_golds)

    def precision(self) -> float | None:
        if not self.preds and not self.golds:
            return None
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0.0

    def recall(self) -> float | None:
        if not self.preds and not self.golds:
            return None
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 1.0

    def f1(self) -> float | None:
        if not self.preds and not self.golds:
            return None
        p = self.precision()
        r = self.recall()
        if p is None or r is None:
            return None
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        return f1


def fuzzy_similarity(a: str | None, b: str | None) -> float:
    """Token-sort ratio, normalised to 0-1. Returns 0 if either value is None."""
    if not a or not b:
        return 0.0
    return fuzz.token_sort_ratio(str(a), str(b)) / 100.0


def exact_similarity(a: Any, b: Any) -> float:
    """Case-insensitive exact match for scalar fields."""
    if a is None and b is None:
        return 1.0
    if a is None or b is None:
        return 0.0
    return 1.0 if str(a).strip().lower() == str(b).strip().lower() else 0.0


def dict_similarity(
    pred_dict: dict[str, Any],
    gold_dict: dict[str, Any],
    similarity_mapping: dict[str, Any],
) -> float | None:
    """
    Average similarity across keys in two dicts.
    similarity_mapping specifies which similarity function to use for each key. (e.g. {"name": fuzzy_similarity, "id": exact_similarity})
    """
    if not pred_dict and not gold_dict:
        return None

    scores = []
    if not similarity_mapping:
        logger.error("No similarity mapping provided, skipping dict similarity")
        return None

    for key, sim_fn in similarity_mapping.items():
        if pred_dict.get(key) and gold_dict.get(key):
            scores.append(sim_fn(pred_dict[key], gold_dict[key]))

    return max(scores) if scores else 0.0


def greedy_match(
    preds: list[T],
    golds: list[T],
    similarity_fn: Callable[[T, T], float | None],
    threshold: float = SIMILARITY_THRESHOLD,
) -> tuple[list[tuple[T, T]], list[T], list[T]]:
    """
    Greedy bipartite matching (highest similarity first).

    Returns:
        matched: list of (pred, gold) pairs
        unmatched_preds: hallucinated entities
        unmatched_golds: missed entities
    """
    if not preds and not golds:
        return [], [], []

    # Build score matrix
    scores: list[tuple[float, int, int]] = []
    for i, pred in enumerate(preds):
        for j, gold in enumerate(golds):
            score = similarity_fn(pred, gold)
            if score and score >= threshold:
                scores.append((score, i, j))

    # Sort by similarity score in descending order
    scores.sort(key=lambda x: -x[0])

    used_preds: set[int] = set()
    used_golds: set[int] = set()
    matched: list[tuple[T, T]] = []

    for _, i, j in scores:
        if i not in used_preds and j not in used_golds:
            matched.append((preds[i], golds[j]))
            used_preds.add(i)
            used_golds.add(j)

    unmatched_preds = [pred for i, pred in enumerate(preds) if i not in used_preds]
    unmatched_golds = [gold for j, gold in enumerate(golds) if j not in used_golds]
    return matched, unmatched_preds, unmatched_golds


def dict_matching(
    pred_dicts: list[dict[str, Any]],
    gold_dicts: list[dict[str, Any]],
    similarity_mapping: dict[str, Any],
    matching_threshold: float = SIMILARITY_THRESHOLD,
) -> tuple[list[tuple[dict[str, Any], dict[str, Any]]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Matching between two lists of dicts (order-insensitive) based on similarity_mapping for each key."""

    def _similarity(p: dict[str, Any], g: dict[str, Any]) -> float | None:
        return dict_similarity(p, g, similarity_mapping)

    return greedy_match(pred_dicts, gold_dicts, similarity_fn=_similarity, threshold=matching_threshold)


def field_list_matching(
    matching_parents: list[tuple[dict[str, Any], dict[str, Any]]], field: str, parent_name_field: str = "name"
) -> tuple[list[tuple[Any, Any]], list[Any], list[Any]]:
    """Matching between two lists of str (order-insensitive) based on a specific field in the dicts."""
    field_list: list[tuple[str, set, set]] = []
    for pred, gold in matching_parents:
        _parent = gold.get(parent_name_field, "?")
        _pred = pred.get(field, [])
        _gold = gold.get(field, [])
        if not _pred and not _gold:
            continue
        field_list.append((_parent, set(_pred), set(_gold)))

    matched: list[tuple[str, set]] = []
    unmatched_preds: list[tuple[str, set]] = []
    unmatched_golds: list[tuple[str, set]] = []

    for parent, pred, gold in field_list:
        intersection = pred.intersection(gold)
        pred_difference = pred.difference(gold)
        gold_difference = gold.difference(pred)

        if intersection:
            matched.append((parent, intersection))

        if pred_difference:
            unmatched_preds.append((parent, pred_difference))

        if gold_difference:
            unmatched_golds.append((parent, gold_difference))

    return matched, unmatched_preds, unmatched_golds
