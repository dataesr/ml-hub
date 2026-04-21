from rapidfuzz import fuzz
from typing import Any
from pydantic import BaseModel, Field
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.85


class Similarity(BaseModel):
    preds: list = Field(default_factory=list)
    golds: list = Field(default_factory=list)
    matched: list[tuple[str, str]] = Field(default_factory=list)
    unmatched_preds: list[str] = Field(default_factory=list)
    unmatched_golds: list[str] = Field(default_factory=list)
    tp: int = 0
    fp: int = 0
    fn: int = 0

    def __init__(self, preds: list, golds: list, similarity_fn=None, threshold: float = SIMILARITY_THRESHOLD):
        super().__init__(preds=preds, golds=golds)
        sim_fn = similarity_fn or exact_similarity
        self.matched, self.unmatched_preds, self.unmatched_golds = greedy_match(preds, golds, sim_fn, threshold)
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
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0.0

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


def list_matching(
    pred_list: list[str], gold_list: list[str], similarity_fn=None, threshold: float = SIMILARITY_THRESHOLD
) -> tuple[list[tuple[str, str]], list[str], list[str]]:
    if not pred_list and not gold_list:
        return [], [], []

    sim_fn = similarity_fn or exact_similarity

    scores: list[tuple[float, int, int]] = []
    for i, pred in enumerate(pred_list):
        for j, gold in enumerate(gold_list):
            score = sim_fn(pred, gold)
            if score >= threshold:
                scores.append((score, i, j))

    # Sort by similarity score in descending order
    scores.sort(key=lambda x: -x[0])

    used_preds: set[int] = set()
    used_golds: set[int] = set()
    matched: list[tuple[str, str]] = []

    for _, i, j in scores:
        if i not in used_preds and j not in used_golds:
            matched.append((pred_list[i], gold_list[j]))
            used_preds.add(i)
            used_golds.add(j)

    unmatched_preds = [pred for i, pred in enumerate(pred_list) if i not in used_preds]
    unmatched_golds = [gold for j, gold in enumerate(gold_list) if j not in used_golds]

    return matched, unmatched_preds, unmatched_golds


def list_similarity(
    pred_list: list[str],
    gold_list: list[str],
    similarity_fn=None,
    threshold: float = SIMILARITY_THRESHOLD,
) -> Any:
    """
    Similarity (precision, recall, f1, unmatched_pred, unmatched_gold) between two lists of strings (order-insensitive).
    Uses similarity_fn to compare individual elements (defaults to exact_similarity).
    """
    if not gold_list and not pred_list:
        return None, None, None, [], []

    sim_fn = similarity_fn or exact_similarity

    matched, unmatched_preds, unmatched_golds = list_matching(pred_list, gold_list, sim_fn, threshold)
    tp = len(matched)
    fp = len(unmatched_preds)
    fn = len(unmatched_golds)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)

    return precision, recall, f1, unmatched_preds, unmatched_golds


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

    keys = similarity_mapping.keys()
    for key in keys:
        if pred_dict.get(key) and gold_dict.get(key):
            sim_fn = similarity_mapping[key]
            scores.append(sim_fn(pred_dict[key], gold_dict[key]))

    return max(scores) if scores else 0.0


def greedy_match(
    preds: list[dict[str, Any]],
    golds: list[dict[str, Any]],
    similarity_fn,
    threshold: float = SIMILARITY_THRESHOLD,
) -> tuple[list[tuple[dict, dict]], list[dict], list[dict]]:
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
            if score >= threshold:
                scores.append((score, i, j))

    # Sort by similarity score in descending order
    scores.sort(key=lambda x: -x[0])

    used_preds: set[int] = set()
    used_golds: set[int] = set()
    matched: list[tuple[dict, dict]] = []

    for _, i, j in scores:
        if i not in used_preds and j not in used_golds:
            matched.append((preds[i], golds[j]))
            used_preds.add(i)
            used_golds.add(j)

    unmatched_preds = [pred for i, pred in enumerate(preds) if i not in used_preds]
    unmatched_golds = [gold for j, gold in enumerate(golds) if j not in used_golds]
    return matched, unmatched_preds, unmatched_golds


def weighted_score(scores: dict[str, float], weights: dict[str, float]) -> float:
    total_w = sum(weights.get(k, 0) for k in scores)
    if total_w == 0:
        return 0.0
    return sum(scores[k] * weights.get(k, 0) for k in scores) / total_w
