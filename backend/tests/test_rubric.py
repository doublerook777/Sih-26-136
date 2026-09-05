import json
import os
import pytest
from app.engines.rubric import validate_rubric, REQUIRED_KEYS


def test_valid_match_rubric():
    weights = {
        "technology_match": 30,
        "domain_experience": 20,
        "past_projects": 15,
        "eligibility": 15,
        "cost_fit": 10,
        "scalability": 10,
    }
    # Should not raise
    validate_rubric(weights, "match")


def test_valid_evaluation_rubric():
    weights = {
        "technical_feasibility": 25,
        "innovation": 15,
        "cost_effectiveness": 15,
        "scalability": 15,
        "security": 10,
        "implementation_capability": 10,
        "social_impact": 10,
    }
    # Should not raise
    validate_rubric(weights, "evaluation")


def test_rubric_sum_not_100_raises():
    weights = {
        "technology_match": 25,
        "domain_experience": 20,
        "past_projects": 15,
        "eligibility": 15,
        "cost_fit": 10,
        "scalability": 10,  # sum = 95
    }
    with pytest.raises(ValueError, match="weights must sum to 100"):
        validate_rubric(weights, "match")


def test_rubric_misspelled_key_raises():
    weights = {
        "tech_match": 30,  # misspelled
        "domain_experience": 20,
        "past_projects": 15,
        "eligibility": 15,
        "cost_fit": 10,
        "scalability": 10,
    }
    with pytest.raises(ValueError, match="bad criteria"):
        validate_rubric(weights, "match")


def test_rubric_missing_and_extra_key_raises():
    weights = {
        "technology_match": 30,
        "domain_experience": 20,
        "past_projects": 15,
        "eligibility": 15,
        "cost_fit": 10,
        "custom_key": 10,  # extra key, scalability missing
    }
    with pytest.raises(ValueError, match="bad criteria"):
        validate_rubric(weights, "match")


def test_unknown_kind_raises():
    weights = {
        "technology_match": 30,
        "domain_experience": 20,
        "past_projects": 15,
        "eligibility": 15,
        "cost_fit": 10,
        "scalability": 10,
    }
    with pytest.raises(ValueError, match="unknown rubric kind"):
        validate_rubric(weights, "unknown_kind")


def test_all_seeded_rubrics_pass_validation():
    seed_file = os.path.join(os.path.dirname(__file__), "..", "seed_data", "rubrics.json")
    with open(seed_file, "r") as f:
        rubrics = json.load(f)

    assert len(rubrics) == 6, "Expected 6 seeded rubrics"
    for rubric in rubrics:
        kind = rubric["kind"]
        weights = {criterion["key"]: criterion["weight"] for criterion in rubric["criteria"]}
        # Must validate cleanly without exception
        validate_rubric(weights, kind)
