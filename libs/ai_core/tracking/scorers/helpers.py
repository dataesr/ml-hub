from rapidfuzz import fuzz
from typing import Any
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.85


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


def list_f1_similarity(
    pred_list: list[str],
    gold_list: list[str],
    similarity_fn=None,
    threshold: float = SIMILARITY_THRESHOLD,
) -> float:
    """
    Token-level F1 between two lists of strings (order-insensitive).
    Uses similarity_fn to compare individual elements (defaults to exact_similarity).
    """
    pred_list = [x for x in (pred_list or []) if x]
    gold_list = [x for x in (gold_list or []) if x]

    if not gold_list and not pred_list:
        return 1.0
    if not gold_list or not pred_list:
        return 0.0

    sim_fn = similarity_fn or (lambda a, b: exact_similarity(a, b))

    tp_pred = sum(1 for p in pred_list if any(sim_fn(p, g) >= threshold for g in gold_list))
    tp_gold = sum(1 for g in gold_list if any(sim_fn(g, p) >= threshold for p in pred_list))
    precision = tp_pred / len(pred_list)
    recall = tp_gold / len(gold_list)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def dict_similarity(
    pred_dict: dict[str, Any],
    gold_dict: dict[str, Any],
    similarity_mapping: dict[str, Any],
) -> float:
    """
    Average similarity across keys in two dicts.
    similarity_mapping specifies which similarity function to use for each key. (e.g. {"name": fuzzy_similarity, "id": exact_similarity})
    """
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
    preds: list[dict],
    golds: list[dict],
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
