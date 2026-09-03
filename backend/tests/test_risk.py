import pytest
from app.engines.risk import (
    calculate_risk_score,
    overall_risk_level,
    calculate_security_score,
    STANDARD_SECURITY_KEYS,
)


def test_calculate_risk_score():
    assert calculate_risk_score(3, 4) == 12
    assert calculate_risk_score(1, 1) == 1
    assert calculate_risk_score(5, 5) == 25
    assert calculate_risk_score(2, 5) == 10
    # Clamping behavior
    assert calculate_risk_score(0, 6) == 5  # clamped to (1, 5)


def test_overall_risk_level_thresholds():
    # Low: < 8
    assert overall_risk_level([1, 4, 7]) == "low"
    assert overall_risk_level([7]) == "low"

    # Medium: 8 to 15 inclusive
    assert overall_risk_level([4, 12, 6]) == "medium"
    assert overall_risk_level([8]) == "medium"
    assert overall_risk_level([15]) == "medium"

    # High: > 15
    assert overall_risk_level([4, 16, 2]) == "high"
    assert overall_risk_level([25]) == "high"
    assert overall_risk_level([12, 18, 9]) == "high"


def test_overall_risk_level_empty_and_edge_cases():
    assert overall_risk_level([]) == "low"
    assert overall_risk_level([None]) == "low"


def test_security_score_all_passed():
    checklist = {k: True for k in STANDARD_SECURITY_KEYS}
    result = calculate_security_score(checklist)
    assert result["score"] == 100.0
    assert result["security_status"] == "passed"
    assert result["passed_count"] == 8
    assert result["total_count"] == 8
    assert result["failed"] == []


def test_security_score_single_failed_remediation():
    checklist = {
        "authentication": True,
        "authorization": True,
        "data_encryption": True,
        "secure_api": True,
        "data_backup": True,
        "vulnerability_assessment": True,
        "access_logging": True,
        "incident_response_plan": False,
    }
    result = calculate_security_score(checklist)
    assert result["score"] == 87.5
    assert result["security_status"] == "needs_remediation"
    assert result["passed_count"] == 7
    assert result["total_count"] == 8
    assert result["failed"] == ["incident_response_plan"]


def test_security_score_multiple_failed_preserves_order():
    checklist = {
        "authentication": True,
        "authorization": False,
        "data_encryption": True,
        "secure_api": False,
        "data_backup": True,
        "vulnerability_assessment": True,
        "access_logging": False,
        "incident_response_plan": True,
    }
    result = calculate_security_score(checklist)
    assert result["score"] == 62.5
    assert result["security_status"] == "needs_remediation"
    assert result["passed_count"] == 5
    assert result["failed"] == ["authorization", "secure_api", "access_logging"]
