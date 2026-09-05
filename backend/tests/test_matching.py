"""
Unit and integration tests for Startup Matching Engine (SIH 26136).
Validates 6-factor calculations, weight configurability, seed data rankings,
and explanation generation.
"""
import copy
import json
import os
import pytest

from app.engines.matching import (
    score_match,
    _compute_technology_match,
    _compute_domain_experience,
    _compute_past_projects,
    _compute_cost_fit,
    _compute_scalability,
)
from app.engines.eligibility import check_eligibility


@pytest.fixture
def default_weights():
    return {
        "technology_match": 30,
        "domain_experience": 20,
        "past_projects": 15,
        "eligibility": 15,
        "cost_fit": 10,
        "scalability": 10,
    }


@pytest.fixture
def low_budget_weights():
    return {
        "technology_match": 25,
        "domain_experience": 15,
        "past_projects": 10,
        "eligibility": 15,
        "cost_fit": 25,
        "scalability": 10,
    }


@pytest.fixture
def sample_water_challenge():
    return {
        "id": 1,
        "title": "Reduce Municipal Water Leakage",
        "sector": "water",
        "budget": 1000000,
        "required_tech": ["iot", "sensors", "analytics", "gis"],
    }


@pytest.fixture
def sample_aquasense():
    return {
        "id": 1,
        "name": "AquaSense Systems",
        "sector": "water",
        "tech_tags": ["iot", "sensors", "analytics", "gis", "ai"],
        "team_size": 18,
        "past_projects": [
            {"name": "Pune Water Pilot", "sector": "water", "year": 2024},
            {"name": "PCMC DMA Project", "sector": "water", "year": 2023},
            {"name": "Surat Audit", "sector": "water", "year": 2022},
        ],
    }


# ---------------------------------------------------------------------------
# Factor Isolation Tests
# ---------------------------------------------------------------------------

def test_factor_technology_match_exact_and_disjoint():
    # Identical tech tags -> 100.0
    req = ["iot", "sensors", "analytics"]
    tags = ["iot", "sensors", "analytics"]
    assert _compute_technology_match(req, tags) == 100.0

    # Disjoint tech tags -> 0.0
    disjoint_tags = ["robotics", "automation"]
    assert _compute_technology_match(req, disjoint_tags) == 0.0

    # Partial overlap
    partial_tags = ["iot", "cloud"]
    score = _compute_technology_match(req, partial_tags)
    assert 0.0 < score < 100.0


def test_factor_domain_experience_exact_adjacent_unrelated():
    assert _compute_domain_experience("water", "water") == 100.0
    assert _compute_domain_experience("water", "waste") == 60.0
    assert _compute_domain_experience("waste", "transport") == 60.0
    assert _compute_domain_experience("water", "healthcare") == 20.0
    assert _compute_domain_experience("water", "transport") == 20.0


def test_factor_past_projects_normalization():
    # 0 matching projects -> 0.0
    assert _compute_past_projects("water", []) == 0.0
    assert _compute_past_projects("water", [{"sector": "healthcare"}]) == 0.0

    # 1 matching project -> 33.3
    p1 = [{"sector": "water"}]
    assert round(_compute_past_projects("water", p1), 1) == 33.3

    # 2 matching projects -> 66.7
    p2 = [{"sector": "water"}, {"sector": "water"}]
    assert round(_compute_past_projects("water", p2), 1) == 66.7

    # 3 matching projects -> 100.0
    p3 = [{"sector": "water"}, {"sector": "water"}, {"sector": "water"}]
    assert _compute_past_projects("water", p3) == 100.0

    # 4 matching projects -> capped at 100.0
    p4 = p3 + [{"sector": "water"}]
    assert _compute_past_projects("water", p4) == 100.0


def test_factor_cost_fit_calculations():
    budget = 1000000

    # Exact match -> 100.0
    score, neutral = _compute_cost_fit(budget, 1000000)
    assert score == 100.0
    assert neutral is False

    # 15% under budget (quote 850,000) -> 85.0
    score, neutral = _compute_cost_fit(budget, 850000)
    assert score == 85.0
    assert neutral is False

    # 20% over budget (quote 1,200,000) -> 80.0
    score, neutral = _compute_cost_fit(budget, 1200000)
    assert score == 80.0
    assert neutral is False

    # Missing quote -> neutral score 75.0, neutral flag True
    score, neutral = _compute_cost_fit(budget, None)
    assert score == 75.0
    assert neutral is True


def test_factor_scalability_formula():
    # Small team (5) + 1 deployment -> 12.5 + 16.7 = 29.2
    score_small = _compute_scalability(team_size=5, past_projects=[{"sector": "water"}])
    assert 25.0 <= score_small <= 35.0

    # Full capacity: team 20+ and 3+ deployments -> 50 + 50 = 100.0
    score_max = _compute_scalability(team_size=25, past_projects=[{}, {}, {}, {}])
    assert score_max == 100.0


# ---------------------------------------------------------------------------
# End-to-End Match Scoring & Contract Integrity
# ---------------------------------------------------------------------------

def test_score_match_returns_expected_contract_shape(sample_water_challenge, sample_aquasense, default_weights):
    result = score_match(
        challenge=sample_water_challenge,
        startup=sample_aquasense,
        weights=default_weights,
        eligibility={"eligible": True},
        quote=850000,
    )

    # Top-level keys must match exactly
    assert "match_score" in result
    assert "match_breakdown" in result
    assert "rubric_snapshot" in result
    assert "explanation" in result

    assert isinstance(result["match_score"], float)
    assert result["match_score"] > 85.0

    breakdown = result["match_breakdown"]
    expected_factors = {
        "technology_match",
        "domain_experience",
        "past_projects",
        "eligibility",
        "cost_fit",
        "scalability",
    }
    assert set(breakdown.keys()) == expected_factors
    assert breakdown["domain_experience"] == 100.0
    assert breakdown["past_projects"] == 100.0
    assert breakdown["eligibility"] == 100.0
    assert breakdown["cost_fit"] == 85.0


def test_rubric_snapshot_is_an_isolated_copy(sample_water_challenge, sample_aquasense, default_weights):
    weights_copy = copy.deepcopy(default_weights)
    result = score_match(
        challenge=sample_water_challenge,
        startup=sample_aquasense,
        weights=weights_copy,
    )

    # Mutate the original dictionary after the call
    weights_copy["technology_match"] = 999
    weights_copy["custom_injected_key"] = 123

    # Snapshot must remain untampered
    assert result["rubric_snapshot"]["technology_match"] == 30
    assert "custom_injected_key" not in result["rubric_snapshot"]


def test_ineligible_startup_gets_zero_eligibility_score(sample_water_challenge, sample_aquasense, default_weights):
    result = score_match(
        challenge=sample_water_challenge,
        startup=sample_aquasense,
        weights=default_weights,
        eligibility={"eligible": False},
        quote=850000,
    )

    assert result["match_breakdown"]["eligibility"] == 0.0


def test_missing_quote_produces_neutral_cost_and_explains(sample_water_challenge, sample_aquasense, default_weights):
    result = score_match(
        challenge=sample_water_challenge,
        startup=sample_aquasense,
        weights=default_weights,
        quote=None,
    )

    assert result["match_breakdown"]["cost_fit"] == 75.0
    assert "neutral cost fit" in result["explanation"].lower()


def test_perfect_match_scores_near_100_and_poor_match_scores_low(sample_water_challenge, default_weights):
    perfect_startup = {
        "name": "Perfect Water Tech",
        "sector": "water",
        "tech_tags": ["iot", "sensors", "analytics", "gis"],
        "team_size": 25,
        "past_projects": [{"sector": "water"}, {"sector": "water"}, {"sector": "water"}],
    }
    poor_startup = {
        "name": "Unrelated Clinic",
        "sector": "healthcare",
        "tech_tags": ["cloud"],
        "team_size": 2,
        "past_projects": [{"sector": "healthcare"}],
    }

    res_perfect = score_match(
        challenge=sample_water_challenge,
        startup=perfect_startup,
        weights=default_weights,
        eligibility={"eligible": True},
        quote=1000000,
    )
    res_poor = score_match(
        challenge=sample_water_challenge,
        startup=poor_startup,
        weights=default_weights,
        eligibility={"eligible": False},
        quote=2500000,
    )

    assert res_perfect["match_score"] >= 95.0
    assert res_poor["match_score"] < 40.0


# ---------------------------------------------------------------------------
# Reweighting / Configurable Rubric Test
# ---------------------------------------------------------------------------

def test_reweighting_changes_startup_ranking_order():
    """
    Demonstrates rubric configurability:
    Startup A (Cheap Startup) has 1 past project (33.3) but an exact budget quote (quote=1,000,000 -> 100.0).
    Startup B (Established Startup) has 3 past projects (100.0) but an expensive quote (quote=1,500,000 -> 50.0).

    Under 'Default (PS baseline)': past_projects=15%, cost_fit=10%. Established Startup wins.
    Under 'Low-budget municipal': past_projects=10%, cost_fit=25%. Cheap Startup wins.
    """
    challenge = {
        "sector": "water",
        "budget": 1000000,
        "required_tech": ["iot", "sensors"],
    }

    cheap_startup = {
        "name": "Cheap Tech",
        "sector": "water",
        "tech_tags": ["iot", "sensors"],
        "team_size": 10,
        "past_projects": [{"sector": "water"}],  # 1 project -> 33.3
        "quote": 1000000,  # Exact budget -> cost_fit = 100.0
    }

    established_startup = {
        "name": "Established Enterprise",
        "sector": "water",
        "tech_tags": ["iot", "sensors"],
        "team_size": 10,
        "past_projects": [{"sector": "water"}, {"sector": "water"}, {"sector": "water"}],  # 3 projects -> 100.0
        "quote": 1500000,  # 50% over budget -> cost_fit = 50.0
    }

    default_rubric_weights = {
        "technology_match": 30,
        "domain_experience": 20,
        "past_projects": 15,
        "eligibility": 15,
        "cost_fit": 10,
        "scalability": 10,
    }

    low_budget_rubric_weights = {
        "technology_match": 25,
        "domain_experience": 15,
        "past_projects": 10,
        "eligibility": 15,
        "cost_fit": 25,
        "scalability": 10,
    }

    # 1. Under Default Rubric
    score_cheap_def = score_match(challenge, cheap_startup, default_rubric_weights)["match_score"]
    score_est_def = score_match(challenge, established_startup, default_rubric_weights)["match_score"]

    assert score_est_def > score_cheap_def, (
        f"Expected Established ({score_est_def}) > Cheap ({score_cheap_def}) under Default Rubric"
    )

    # 2. Under Low-Budget Rubric
    score_cheap_low = score_match(challenge, cheap_startup, low_budget_rubric_weights)["match_score"]
    score_est_low = score_match(challenge, established_startup, low_budget_rubric_weights)["match_score"]

    assert score_cheap_low > score_est_low, (
        f"Expected Cheap ({score_cheap_low}) > Established ({score_est_low}) under Low-Budget Rubric"
    )


# ---------------------------------------------------------------------------
# Seed Data Integration & Spread Tests
# ---------------------------------------------------------------------------

def test_seed_data_scoring_spread_and_top_candidate():
    """
    Scores all 20 seeded startups against Challenge 1 (Municipal Water Leakage).
    Verifies that:
    1. Scores produce a realistic spread across all 20 startups (not all clustered).
    2. AquaSense Systems is the top-ranked water startup.
    """
    seed_dir = os.path.join(os.path.dirname(__file__), "..", "seed_data")
    with open(os.path.join(seed_dir, "startups.json")) as f:
        startups = json.load(f)
    with open(os.path.join(seed_dir, "challenges.json")) as f:
        challenges = json.load(f)
    with open(os.path.join(seed_dir, "rubrics.json")) as f:
        rubrics = json.load(f)

    water_challenge = challenges[0]
    default_rubric = next(r for r in rubrics if r["id"] == water_challenge["match_rubric_id"])
    weights = {c["key"]: c["weight"] for c in default_rubric["criteria"]}

    scores = []
    for s in startups:
        elig_res = check_eligibility(water_challenge, s)
        res = score_match(
            challenge=water_challenge,
            startup=s,
            weights=weights,
            eligibility=elig_res,
            quote=s.get("quote"),
        )
        scores.append({
            "name": s["name"],
            "sector": s["sector"],
            "eligible": elig_res["eligible"],
            "match_score": res["match_score"],
        })

    # Sort by eligibility then match score descending
    scores.sort(key=lambda x: (x["eligible"], x["match_score"]), reverse=True)

    # Check top startup
    top_startup = scores[0]
    assert top_startup["name"] == "AquaSense Systems"
    assert top_startup["eligible"] is True
    assert top_startup["match_score"] >= 90.0

    # Verify score spread (difference between top and bottom eligible/ineligible must be > 30)
    highest_score = max(s["match_score"] for s in scores)
    lowest_score = min(s["match_score"] for s in scores)
    score_range = highest_score - lowest_score
    assert score_range > 30.0, f"Expected realistic score spread > 30 points, got {score_range}"
