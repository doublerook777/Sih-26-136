"""
Performance Scoring Engine for ProcuraAI (SIH 26136).
Implements KPI achievement rollup and final composite scoring per Roadmap Section 7b.

Pure functional module: Zero database imports, zero network calls.
"""
from typing import Any, Dict, List, Union

FINAL_SCORE_WEIGHTS = {
    "technical": 30,
    "cost": 20,
    "impact": 20,
    "scalability": 15,
    "security": 15,
}


def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def achievement(kpi: Union[Dict[str, Any], Any]) -> float:
    """
    Calculates individual KPI achievement fraction (0.0 to 1.2, capped at 120%).

    Formula (Roadmap 7b):
      span = abs(target - baseline)
      gain = abs(achieved - baseline)
      If moving in wrong direction, gain is negated.
      Result clamped to [0.0, 1.2].

    Args:
        kpi: Dict or object containing 'baseline', 'target', 'achieved', and 'direction'
             ('lower_is_better' | 'higher_is_better').

    Returns:
        float fraction between 0.0 and 1.2.
    """
    baseline = float(_get_val(kpi, "baseline", 0.0))
    target = float(_get_val(kpi, "target", 0.0))
    achieved = _get_val(kpi, "achieved", None)
    direction = str(_get_val(kpi, "direction", "higher_is_better")).lower()

    if achieved is None:
        return 0.0

    achieved = float(achieved)
    span = abs(target - baseline)

    if span == 0:
        if direction == "lower_is_better":
            return 1.0 if achieved <= target else 0.0
        return 1.0 if achieved >= target else 0.0

    gain = abs(achieved - baseline)
    wrong_way = (direction == "lower_is_better" and achieved > baseline) or \
                (direction == "higher_is_better" and achieved < baseline)

    if wrong_way:
        gain = -gain

    return max(0.0, min(gain / span, 1.2))


def achievement_percentage(kpi: Union[Dict[str, Any], Any]) -> float:
    """
    Returns KPI achievement as a percentage between 0.0 and 120.0.
    """
    return round(achievement(kpi) * 100.0, 1)


def final_score(kpis: List[Union[Dict[str, Any], Any]], security_score: float) -> Dict[str, Any]:
    """
    Rolls up KPIs across categories and combines with cybersecurity audit score
    to produce the definitive composite final pilot score.

    Category Weights (Hardcoded per Roadmap Section 7):
      - technical: 30%
      - cost: 20%
      - impact: 20%
      - scalability: 15%
      - security: 15%

    Args:
        kpis: List of KPI dictionaries or objects, each with 'category' and measurement values.
        security_score: 0-100 float from the 8-item cybersecurity checklist.

    Returns:
        {
            "category_scores": {
                "technical": 79.0,
                "cost": 87.0,
                "impact": 120.0,
                "scalability": 89.0,
                "security": 96.0
            },
            "weights": {
                "technical": 30,
                "cost": 20,
                "impact": 20,
                "scalability": 15,
                "security": 15
            },
            "final_score": 92.9
        }
    """
    categories = ["technical", "cost", "impact", "scalability"]
    category_kpi_scores: Dict[str, List[float]] = {cat: [] for cat in categories}

    for kpi in kpis:
        cat = str(_get_val(kpi, "category", "")).lower()
        if cat in category_kpi_scores:
            # Check if achievement or score is pre-computed on the object
            raw_ach = _get_val(kpi, "achievement", None)
            if raw_ach is not None:
                # If achievement is already given as 0-120 percentage
                val = float(raw_ach)
                if val <= 1.2 and val > 0:  # fraction converted to percentage
                    val = val * 100.0
            else:
                val = achievement_percentage(kpi)
            category_kpi_scores[cat].append(val)

    category_scores: Dict[str, float] = {}
    for cat in categories:
        scores = category_kpi_scores[cat]
        if scores:
            category_scores[cat] = round(sum(scores) / len(scores), 1)
        else:
            # Sensible default for empty categories: 100.0 (unconstrained)
            category_scores[cat] = 100.0

    # Security score comes directly from the cybersecurity checklist
    sec_score = round(max(0.0, min(100.0, float(security_score))), 1)
    category_scores["security"] = sec_score

    # Compute weighted final score
    weighted_sum = sum(
        category_scores[cat] * (FINAL_SCORE_WEIGHTS[cat] / 100.0)
        for cat in FINAL_SCORE_WEIGHTS
    )
    total_final = round(weighted_sum + 1e-9, 1)

    return {
        "category_scores": category_scores,
        "weights": dict(FINAL_SCORE_WEIGHTS),
        "final_score": total_final,
    }
