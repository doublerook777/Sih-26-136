"""
Rubric validation engine for ProcuraAI.
Pure functions for validating match and evaluation scoring rubrics.
Zero database imports, zero network calls.
"""
from typing import Dict, Any, Set

REQUIRED_KEYS: Dict[str, Set[str]] = {
    "match": {
        "technology_match",
        "domain_experience",
        "past_projects",
        "eligibility",
        "cost_fit",
        "scalability",
    },
    "evaluation": {
        "technical_feasibility",
        "innovation",
        "cost_effectiveness",
        "scalability",
        "security",
        "implementation_capability",
        "social_impact",
    },
}


def validate_rubric(weights: Dict[str, float | int], kind: str) -> None:
    """
    Validates that a rubric's weights dictionary matches the required criteria
    keys for its kind ('match' or 'evaluation') and that weights sum to 100.

    Raises ValueError if criteria are missing/extra, if kind is unknown, or if sum != 100.
    """
    if kind not in REQUIRED_KEYS:
        raise ValueError(f"unknown rubric kind: '{kind}'. Expected 'match' or 'evaluation'.")

    weight_keys = set(weights.keys())
    required = REQUIRED_KEYS[kind]

    if weight_keys != required:
        missing = required - weight_keys
        extra = weight_keys - required
        raise ValueError(f"bad criteria. missing={sorted(list(missing))} extra={sorted(list(extra))}")

    total_weight = sum(weights.values())
    if abs(total_weight - 100.0) > 0.01:
        raise ValueError(f"weights must sum to 100, got {total_weight}")
