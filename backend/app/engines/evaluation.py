"""
Expert Evaluation Scoring Engine for ProcuraAI (SIH 26136).
Pure functional implementation: Zero database imports, zero network calls.

Scores individual expert evaluations against configurable rubrics and
computes multi-expert weighted averages.
"""
from typing import Any, Dict, List, Optional
from app.engines.rubric import validate_rubric, REQUIRED_KEYS


def score_evaluation(scores: Dict[str, Any], weights: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scores an expert's evaluation against a configured evaluation rubric.

    Args:
        scores: Dict mapping all 7 evaluation criteria keys to numeric scores (0-100).
        weights: Dict mapping the same 7 criteria keys to percentage weights (summing to 100).

    Returns:
        {
            "weighted_total": 87.6,
            "rubric_snapshot": {...copied weights...}
        }

    Raises:
        ValueError: If weights are invalid (wrong sum or keys) or if scores dictionary
                    is missing required criteria keys, has extra keys, or contains out-of-range values.
    """
    if not isinstance(weights, dict):
        raise ValueError("weights must be a dictionary")
    if not isinstance(scores, dict):
        raise ValueError("scores must be a dictionary")

    # Validate weights structure and sum == 100
    validate_rubric(weights, "evaluation")

    required_keys = REQUIRED_KEYS["evaluation"]
    score_keys = set(scores.keys())

    if score_keys != required_keys:
        missing = sorted(list(required_keys - score_keys))
        extra = sorted(list(score_keys - required_keys))
        raise ValueError(f"bad criteria in scores. missing={missing} extra={extra}")

    # Validate score values (must be numeric and in 0-100)
    for key, val in scores.items():
        if val is None or not isinstance(val, (int, float)) or isinstance(val, bool):
            raise ValueError(f"score for '{key}' must be numeric, got {type(val).__name__}")
        if val < 0.0 or val > 100.0:
            raise ValueError(f"score for '{key}' must be between 0 and 100, got {val}")

    # Calculate weighted total
    total = sum(float(scores[k]) * float(weights[k]) / 100.0 for k in required_keys)
    weighted_total = round(total, 1)

    return {
        "weighted_total": weighted_total,
        "rubric_snapshot": dict(weights)
    }


def average_evaluations(evaluations: List[Any]) -> Dict[str, Any]:
    """
    Averages several expert evaluations for a single application under a shared rubric.

    Args:
        evaluations: List of already-scored evaluation dicts or objects (each containing 'weighted_total').

    Returns:
        {"average_total": 88.0, "evaluation_count": 3}
        or {"average_total": None, "evaluation_count": 0} if list is empty.
    """
    if not evaluations:
        return {
            "average_total": None,
            "evaluation_count": 0
        }

    totals: List[float] = []
    for item in evaluations:
        if isinstance(item, dict):
            val = item.get("weighted_total")
        else:
            val = getattr(item, "weighted_total", None)

        if val is not None and isinstance(val, (int, float)) and not isinstance(val, bool):
            totals.append(float(val))

    if not totals:
        return {
            "average_total": None,
            "evaluation_count": 0
        }

    avg = sum(totals) / len(totals)
    return {
        "average_total": round(avg, 1),
        "evaluation_count": len(totals)
    }
