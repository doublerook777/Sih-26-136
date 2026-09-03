"""
Risk & Security Governance Scoring Engines for ProcuraAI (SIH 26136).
Pure functional implementations: Zero database imports, zero network calls.

Provides:
1. calculate_risk_score(probability, impact)
2. overall_risk_level(risk_scores)
3. calculate_security_score(checklist)
"""
from typing import Any, Dict, List, Optional

# Standard 8-item cybersecurity baseline fields per docs/API.md section 9
STANDARD_SECURITY_KEYS = [
    "authentication",
    "authorization",
    "data_encryption",
    "secure_api",
    "data_backup",
    "vulnerability_assessment",
    "access_logging",
    "incident_response_plan",
]


def calculate_risk_score(probability: int, impact: int) -> int:
    """
    Computes a risk factor score as probability * impact.

    Args:
        probability: Likelihood scale from 1 (rare) to 5 (almost certain).
        impact: Consequence scale from 1 (negligible) to 5 (catastrophic).

    Returns:
        Integer score from 1 to 25.
    """
    prob = max(1, min(5, int(probability)))
    imp = max(1, min(5, int(impact)))
    return prob * imp


def overall_risk_level(risk_scores: List[int]) -> str:
    """
    Evaluates the overall composite risk level for a pilot based on the highest
    individual risk score present.

    Thresholds:
      - "low": highest score < 8 (or empty risk list default)
      - "medium": highest score between 8 and 15 (inclusive)
      - "high": highest score > 15

    Args:
        risk_scores: List of integer risk scores (1-25) for each identified pilot risk.

    Returns:
        "low" | "medium" | "high"
    """
    if not risk_scores:
        return "low"

    valid_scores = [int(s) for s in risk_scores if s is not None]
    if not valid_scores:
        return "low"

    highest = max(valid_scores)

    if highest > 15:
        return "high"
    elif highest >= 8:
        return "medium"
    else:
        return "low"


def calculate_security_score(checklist: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates a pilot's 8-item cybersecurity checklist.

    Args:
        checklist: Dictionary containing boolean checks for security dimensions:
          - authentication
          - authorization
          - data_encryption
          - secure_api
          - data_backup
          - vulnerability_assessment
          - access_logging
          - incident_response_plan

    Returns:
        {
            "security_status": "passed" | "needs_remediation",
            "score": 87.5,
            "passed_count": 7,
            "total_count": 8,
            "failed": ["incident_response_plan"]
        }
    """
    if not isinstance(checklist, dict):
        checklist = {}

    failed = []
    passed_count = 0

    # Determine keys to evaluate: use checklist keys in order if present, or STANDARD_SECURITY_KEYS
    keys_to_check = []
    for k in checklist.keys():
        if k in STANDARD_SECURITY_KEYS and k not in keys_to_check:
            keys_to_check.append(k)
    for k in STANDARD_SECURITY_KEYS:
        if k not in keys_to_check:
            keys_to_check.append(k)

    for key in keys_to_check:
        val = checklist.get(key, False)
        if bool(val) is True:
            passed_count += 1
        else:
            failed.append(key)

    total_count = len(keys_to_check)
    score = round((passed_count / total_count) * 100.0, 1) if total_count > 0 else 0.0
    security_status = "passed" if (passed_count == total_count and total_count > 0) else "needs_remediation"

    return {
        "security_status": security_status,
        "score": score,
        "passed_count": passed_count,
        "total_count": total_count,
        "failed": failed,
    }
