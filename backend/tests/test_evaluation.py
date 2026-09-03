import json
from pathlib import Path
import pytest
from app.engines.evaluation import score_evaluation, average_evaluations


@pytest.fixture
def default_weights():
    return {
        "technical_feasibility": 25,
        "innovation": 15,
        "cost_effectiveness": 15,
        "scalability": 15,
        "security": 10,
        "implementation_capability": 10,
        "social_impact": 10,
    }


@pytest.fixture
def security_weights():
    return {
        "technical_feasibility": 20,
        "innovation": 10,
        "cost_effectiveness": 15,
        "scalability": 15,
        "security": 25,
        "implementation_capability": 10,
        "social_impact": 5,
    }


@pytest.fixture
def real_rubrics():
    rubrics_path = Path(__file__).resolve().parent.parent / "seed_data" / "rubrics.json"
    with open(rubrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {r["name"]: {c["key"]: c["weight"] for c in r["criteria"]} for r in data if r["kind"] == "evaluation"}


def test_perfect_scorecard_scores_100(default_weights):
    perfect_scores = {k: 100 for k in default_weights}
    result = score_evaluation(perfect_scores, default_weights)
    assert result["weighted_total"] == 100.0
    assert result["rubric_snapshot"] == default_weights
    # Ensure rubric_snapshot is a copy, not the same dict reference
    assert result["rubric_snapshot"] is not default_weights


def test_zero_scorecard_scores_0(default_weights):
    zero_scores = {k: 0 for k in default_weights}
    result = score_evaluation(zero_scores, default_weights)
    assert result["weighted_total"] == 0.0


def test_each_criterion_weighted_in_isolation(default_weights):
    """Setting one criterion to 100 and the rest to 0 yields that criterion's weight."""
    for criterion, weight in default_weights.items():
        scores = {k: 0 for k in default_weights}
        scores[criterion] = 100
        result = score_evaluation(scores, default_weights)
        assert result["weighted_total"] == float(weight), f"Failed for criterion: {criterion}"


def test_missing_key_raises_value_error(default_weights):
    scores = {
        "technical_feasibility": 80,
        "innovation": 75,
        "cost_effectiveness": 70,
        "scalability": 85,
        "security": 90,
        "implementation_capability": 80,
        # missing 'social_impact'
    }
    with pytest.raises(ValueError, match="missing.*social_impact"):
        score_evaluation(scores, default_weights)


def test_extra_key_raises_value_error(default_weights):
    scores = {k: 80 for k in default_weights}
    scores["unrecognized_bonus"] = 50
    with pytest.raises(ValueError, match="extra.*unrecognized_bonus"):
        score_evaluation(scores, default_weights)


def test_invalid_score_range_raises_value_error(default_weights):
    scores_high = {k: 80 for k in default_weights}
    scores_high["security"] = 105
    with pytest.raises(ValueError, match="must be between 0 and 100"):
        score_evaluation(scores_high, default_weights)

    scores_low = {k: 80 for k in default_weights}
    scores_low["security"] = -5
    with pytest.raises(ValueError, match="must be between 0 and 100"):
        score_evaluation(scores_low, default_weights)


def test_average_evaluations_three_scores():
    evals = [
        {"weighted_total": 88.0},
        {"weighted_total": 91.0},
        {"weighted_total": 85.0},
    ]
    res = average_evaluations(evals)
    assert res["average_total"] == 88.0
    assert res["evaluation_count"] == 3


def test_average_evaluations_empty_list():
    res = average_evaluations([])
    assert res["average_total"] is None
    assert res["evaluation_count"] == 0


def test_reweighting_proof_changes_outcome(real_rubrics):
    """
    Proves that evaluating the exact same scorecard under 'Default expert panel' vs
    'Security-weighted panel' produces a distinctly different weighted total.
    """
    default_panel = real_rubrics["Default expert panel"]
    security_panel = real_rubrics["Security-weighted panel"]

    # Candidate scorecard with exceptional security (95) but modest technical (60)
    scorecard = {
        "technical_feasibility": 60,
        "innovation": 50,
        "cost_effectiveness": 70,
        "scalability": 70,
        "security": 95,
        "implementation_capability": 75,
        "social_impact": 60,
    }

    res_default = score_evaluation(scorecard, default_panel)
    res_security = score_evaluation(scorecard, security_panel)

    # In default panel: (60*25 + 50*15 + 70*15 + 70*15 + 95*10 + 75*10 + 60*10)/100 = 66.5
    # In security panel: (60*20 + 50*10 + 70*15 + 70*15 + 95*25 + 75*10 + 60*5)/100 = 72.25 -> 72.3
    assert res_default["weighted_total"] == 66.5
    assert res_security["weighted_total"] == 72.2
    assert res_security["weighted_total"] > res_default["weighted_total"]
