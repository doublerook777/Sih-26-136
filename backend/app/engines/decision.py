"""
Procurement Decision & Justification Engine for ProcuraAI (SIH 26136).
Implements deterministic four-way scale-up decisions and explainable audit text.

Pure functional module: Zero database imports, zero network calls.
"""
from typing import Any, Dict


def decide(final_score: float) -> str:
    """
    Evaluates the definitive four-way procurement decision based on hardcoded
    statutory thresholds.

    Thresholds:
      - >= 85.0: "scale" (Approved for statewide/district replication)
      - >= 70.0: "scale_with_modifications" (Approved with corrective refinements)
      - >= 55.0: "extend_pilot" (Additional validation period required)
      - < 55.0:  "reject" (Did not meet minimum procurement thresholds)

    Args:
        final_score: Composite 0-120 score from performance.final_score.

    Returns:
        "scale" | "scale_with_modifications" | "extend_pilot" | "reject"
    """
    score = float(final_score)
    if score >= 85.0:
        return "scale"
    elif score >= 70.0:
        return "scale_with_modifications"
    elif score >= 55.0:
        return "extend_pilot"
    else:
        return "reject"


def justify(
    category_scores: Dict[str, Any],
    decision: str,
    milestones_validated: int,
    security_status: str,
) -> str:
    """
    Generates a clear, explainable justification statement embedding actual quantitative
    performance values from the pilot.

    Args:
        category_scores: Dictionary of category scores (technical, cost, impact, scalability, security).
        decision: One of 'scale', 'scale_with_modifications', 'extend_pilot', 'reject'.
        milestones_validated: Integer count of validated milestones (e.g. 4).
        security_status: 'passed' | 'needs_remediation'.

    Returns:
        String containing precise quantitative justification.
    """
    tech = category_scores.get("technical", 0.0)
    cost = category_scores.get("cost", 0.0)
    impact = category_scores.get("impact", 0.0)
    scale = category_scores.get("scalability", 0.0)
    sec = category_scores.get("security", 0.0)

    ms_text = f"{milestones_validated}/4 milestones verified" if milestones_validated is not None else "milestones verified"
    sec_text = f"cybersecurity audit {security_status} ({sec}%)"

    if decision == "scale":
        return (
            f"Exceeded impact target with score {impact}%, achieved technical reliability of {tech}%, "
            f"cost efficiency of {cost}%, and scalability rating of {scale}%. "
            f"All {ms_text} and {sec_text}. Recommended for accelerated statewide procurement scale."
        )
    elif decision == "scale_with_modifications":
        return (
            f"Demonstrated solid performance with impact score {impact}% and technical score {tech}%, "
            f"with {ms_text}. {sec_text}. Recommended for conditional replication subject to cost and scalability optimizations."
        )
    elif decision == "extend_pilot":
        return (
            f"Partial milestone attainment ({ms_text}) with technical score {tech}% and impact score {impact}%. "
            f"{sec_text}. Recommended for a 60-day pilot extension to complete remaining milestone validation."
        )
    else:
        return (
            f"Failed to meet minimum performance thresholds: impact score {impact}%, technical score {tech}%, "
            f"and cost score {cost}%. Only {ms_text} with {sec_text}. Pilot terminated without replication."
        )
