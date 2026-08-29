import json
import os
import pytest
from app.engines.eligibility import check_eligibility


@pytest.fixture
def base_challenge():
    return {
        "id": 1,
        "title": "Reduce municipal water leakage",
        "sector": "water",
        "budget": 1000000,
        "required_tech": ["iot", "sensors", "analytics", "gis"],
        "eligibility_rules": {
            "registered_startup": True,
            "required_certification": "ISO 9001:2015",
            "min_experience_years": 2,
            "min_technology_overlap": 1,
            "max_quote": 1000000,
            "security_baseline": True,
        },
    }


@pytest.fixture
def perfect_startup():
    return {
        "id": 1,
        "name": "AquaSense",
        "sector": "water",
        "dpiit_number": "DIPP12345",
        "incorporation_year": 2021,  # 5 years exp in 2026
        "certifications": ["ISO 9001:2015", "ISO 27001"],
        "tech_tags": ["iot", "sensors", "analytics"],
        "security_baseline": True,
    }


def test_perfect_startup_passes_all_gates(base_challenge, perfect_startup):
    result = check_eligibility(base_challenge, perfect_startup, quote=850000)
    assert result["eligible"] is True
    report = result["report"]

    assert report["registered_startup"]["passed"] is True
    assert "DIPP12345" in report["registered_startup"]["note"]

    assert report["required_certification"]["passed"] is True
    assert "ISO 9001:2015 present" in report["required_certification"]["note"]

    assert report["min_experience_years"]["passed"] is True
    assert "5 years, needs 2" in report["min_experience_years"]["note"]

    assert report["technology_overlap"]["passed"] is True
    assert "3 of 4 matched" in report["technology_overlap"]["note"]

    assert report["budget_within_range"]["passed"] is True
    assert "quote 8.5L of 10.0L" in report["budget_within_range"]["note"]

    assert report["security_baseline"]["passed"] is True
    assert "self-declared" in report["security_baseline"]["note"]


def test_gate1_fail_missing_dpiit(base_challenge, perfect_startup):
    startup = dict(perfect_startup, dpiit_number=None)
    result = check_eligibility(base_challenge, startup, quote=800000)
    assert result["eligible"] is False
    assert result["report"]["registered_startup"]["passed"] is False
    assert "No DPIIT registration" in result["report"]["registered_startup"]["note"]


def test_gate2_fail_missing_certification(base_challenge, perfect_startup):
    startup = dict(perfect_startup, certifications=["Some Other Cert"])
    result = check_eligibility(base_challenge, startup, quote=800000)
    assert result["eligible"] is False
    assert result["report"]["required_certification"]["passed"] is False
    assert "Missing required certification: ISO 9001:2015" in result["report"]["required_certification"]["note"]


def test_gate3_fail_insufficient_experience(base_challenge, perfect_startup):
    startup = dict(perfect_startup, incorporation_year=2025)  # 1 year in 2026, needs 2
    result = check_eligibility(base_challenge, startup, quote=800000)
    assert result["eligible"] is False
    assert result["report"]["min_experience_years"]["passed"] is False
    assert "1 years, needs 2" in result["report"]["min_experience_years"]["note"]


def test_gate4_fail_zero_tech_overlap(base_challenge, perfect_startup):
    startup = dict(perfect_startup, tech_tags=["robotics", "automation"])
    result = check_eligibility(base_challenge, startup, quote=800000)
    assert result["eligible"] is False
    assert result["report"]["technology_overlap"]["passed"] is False
    assert "0 of 4 matched" in result["report"]["technology_overlap"]["note"]


def test_gate5_fail_quote_exceeds_budget(base_challenge, perfect_startup):
    result = check_eligibility(base_challenge, perfect_startup, quote=1250000)  # budget is 1,000,000
    assert result["eligible"] is False
    assert result["report"]["budget_within_range"]["passed"] is False
    assert "exceeds budget" in result["report"]["budget_within_range"]["note"]


def test_gate6_fail_security_baseline(base_challenge, perfect_startup):
    startup = dict(perfect_startup, security_baseline=False)
    result = check_eligibility(base_challenge, startup, quote=800000)
    assert result["eligible"] is False
    assert result["report"]["security_baseline"]["passed"] is False
    assert "Security baseline not satisfied" in result["report"]["security_baseline"]["note"]


def test_multiple_gates_failing_at_once(base_challenge, perfect_startup):
    startup = dict(
        perfect_startup,
        dpiit_number=None,
        incorporation_year=2025,
        certifications=[],
    )
    result = check_eligibility(base_challenge, startup, quote=1500000)
    assert result["eligible"] is False
    assert result["report"]["registered_startup"]["passed"] is False
    assert result["report"]["required_certification"]["passed"] is False
    assert result["report"]["min_experience_years"]["passed"] is False
    assert result["report"]["budget_within_range"]["passed"] is False


def test_water_startups_spread_against_water_challenge():
    """
    Verifies that for the 5 water startups evaluated against the demo water challenge:
    3 pass (AquaSense, PipeAI, JalShuddh) and 2 fail (HydroTrack on experience, AquaDrain on registration).
    """
    seed_startups_file = os.path.join(os.path.dirname(__file__), "..", "seed_data", "startups.json")
    seed_challenges_file = os.path.join(os.path.dirname(__file__), "..", "seed_data", "challenges.json")

    with open(seed_startups_file) as f:
        startups = json.load(f)
    with open(seed_challenges_file) as f:
        challenges = json.load(f)

    water_challenge = challenges[0]
    water_startups = [s for s in startups if s["sector"] == "water"]
    assert len(water_startups) == 5

    results = {s["name"]: check_eligibility(water_challenge, s) for s in water_startups}

    assert results["AquaSense Systems"]["eligible"] is True
    assert results["PipeAI Technologies"]["eligible"] is True
    assert results["JalShuddh AI"]["eligible"] is True

    assert results["HydroTrack Telemetry"]["eligible"] is False
    assert results["HydroTrack Telemetry"]["report"]["min_experience_years"]["passed"] is False

    assert results["AquaDrain Solutions"]["eligible"] is False
    assert results["AquaDrain Solutions"]["report"]["registered_startup"]["passed"] is False


def test_all_20_startups_baseline_eligibility_spread():
    """
    Verifies that across all 20 startups with standard baseline rules (registration + experience >= 2),
    exactly 12 pass and 8 fail (4 on registration, 4 on experience).
    """
    seed_startups_file = os.path.join(os.path.dirname(__file__), "..", "seed_data", "startups.json")
    with open(seed_startups_file) as f:
        startups = json.load(f)

    baseline_challenge = {
        "required_tech": ["iot", "sensors", "ai", "computer-vision", "analytics", "cloud", "mobile-app", "gis", "telematics", "robotics", "edge-computing", "automation"],
        "eligibility_rules": {
            "registered_startup": True,
            "min_experience_years": 2,
            "min_technology_overlap": 1,
            "security_baseline": True,
        }
    }

    passed_count = 0
    failed_count = 0
    dpiit_fails = 0
    exp_fails = 0

    for s in startups:
        res = check_eligibility(baseline_challenge, s)
        if res["eligible"]:
            passed_count += 1
        else:
            failed_count += 1
            if not res["report"]["registered_startup"]["passed"]:
                dpiit_fails += 1
            if not res["report"]["min_experience_years"]["passed"]:
                exp_fails += 1

    assert len(startups) == 20
    assert passed_count == 12, f"Expected 12 passing startups, got {passed_count}"
    assert failed_count == 8, f"Expected 8 failing startups, got {failed_count}"
    assert dpiit_fails == 4, f"Expected 4 DPIIT fails, got {dpiit_fails}"
    assert exp_fails == 4, f"Expected 4 experience fails, got {exp_fails}"
