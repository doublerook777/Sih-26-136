import pytest
from app.engines.decision import decide, justify


def test_decide_four_outcomes():
    assert decide(90.0) == "scale"
    assert decide(75.0) == "scale_with_modifications"
    assert decide(60.0) == "extend_pilot"
    assert decide(40.0) == "reject"


def test_decide_exact_threshold_boundaries():
    # Exactly 85.0 lands on "scale" (higher tier), 84.9 lands on "scale_with_modifications"
    assert decide(85.0) == "scale"
    assert decide(84.9) == "scale_with_modifications"

    # Exactly 70.0 lands on "scale_with_modifications", 69.9 lands on "extend_pilot"
    assert decide(70.0) == "scale_with_modifications"
    assert decide(69.9) == "extend_pilot"

    # Exactly 55.0 lands on "extend_pilot", 54.9 lands on "reject"
    assert decide(55.0) == "extend_pilot"
    assert decide(54.9) == "reject"


def test_justify_names_real_numbers():
    cat_scores = {
        "technical": 79.0,
        "cost": 87.0,
        "impact": 120.0,
        "scalability": 89.0,
        "security": 96.0,
    }
    justification = justify(
        category_scores=cat_scores,
        decision="scale",
        milestones_validated=4,
        security_status="passed",
    )

    assert "120.0" in justification
    assert "79.0" in justification
    assert "4/4" in justification
    assert "passed" in justification
    assert "scale" in justification.lower()


def test_justify_all_decision_variants():
    cat_scores = {
        "technical": 65.0,
        "cost": 70.0,
        "impact": 75.0,
        "scalability": 60.0,
        "security": 80.0,
    }

    just_mod = justify(cat_scores, "scale_with_modifications", 3, "passed")
    assert "scale_with_modifications" in just_mod or "conditional replication" in just_mod
    assert "75.0" in just_mod

    just_ext = justify(cat_scores, "extend_pilot", 2, "needs_remediation")
    assert "extension" in just_ext
    assert "2/4" in just_ext

    just_rej = justify(cat_scores, "reject", 1, "needs_remediation")
    assert "terminated" in just_rej or "reject" in just_rej
