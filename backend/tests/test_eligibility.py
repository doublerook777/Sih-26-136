import pytest
from backend.app.engines.eligibility import check_eligibility


@pytest.fixture
def sample_challenge():
    return {
        "id": 1,
        "title": "Smart Municipal Water Leak Detection",
        "budget": 1000000,
        "required_tech": ["IoT", "Sensors", "Analytics"],
        "eligibility_rules": {
            "registered_startup": True,
            "required_certification": "ISO 27001",
            "min_experience_years": 2,
            "min_technology_overlap": 2,
            "max_quote": 1000000,
            "security_baseline": True,
        }
    }


@pytest.fixture
def eligible_startup():
    return {
        "id": 3,
        "name": "AquaSense Systems",
        "sector": "Water Management",
        "technologies": ["IoT", "Sensors", "Analytics", "AI"],
        "dpiit_number": "DIPP48291",
        "incorporation_year": 2021,
        "turnover": 6500000,
        "team_size": 18,
        "certifications": ["ISO 9001:2015", "ISO 27001"],
        "past_projects": ["Pune Municipal Smart Water Pilot - Ward 7"],
        "description": "Smart municipal water distribution monitoring platform."
    }


def test_fully_eligible_startup(sample_challenge, eligible_startup):
    result = check_eligibility(sample_challenge, eligible_startup, quote=850000, current_year=2026)
    assert result["eligible"] is True
    assert len(result["failed_reasons"]) == 0
    
    report = result["eligibility_report"]
    assert report["registered_startup"]["passed"] is True
    assert report["registered_startup"]["note"] == "DIPP48291"
    assert report["required_certification"]["passed"] is True
    assert report["min_experience_years"]["passed"] is True
    assert report["technology_overlap"]["passed"] is True
    assert report["budget_within_range"]["passed"] is True
    assert report["security_baseline"]["passed"] is True


def test_missing_dpiit_fails(sample_challenge, eligible_startup):
    startup = dict(eligible_startup)
    startup["dpiit_number"] = None
    startup["dpiit"] = False
    
    result = check_eligibility(sample_challenge, startup, quote=800000, current_year=2026)
    assert result["eligible"] is False
    assert any("DPIIT" in r for r in result["failed_reasons"])
    assert result["eligibility_report"]["registered_startup"]["passed"] is False


def test_missing_certification_fails(sample_challenge, eligible_startup):
    startup = dict(eligible_startup)
    startup["certifications"] = ["ISO 9001:2015"]  # Missing ISO 27001
    
    result = check_eligibility(sample_challenge, startup, quote=800000, current_year=2026)
    assert result["eligible"] is False
    assert any("ISO 27001" in r for r in result["failed_reasons"])
    assert result["eligibility_report"]["required_certification"]["passed"] is False


def test_insufficient_experience_fails(sample_challenge, eligible_startup):
    startup = dict(eligible_startup)
    startup["incorporation_year"] = 2025  # Only 1 year in 2026, requires 2
    
    result = check_eligibility(sample_challenge, startup, quote=800000, current_year=2026)
    assert result["eligible"] is False
    assert any("Experience" in r for r in result["failed_reasons"])
    assert result["eligibility_report"]["min_experience_years"]["passed"] is False


def test_insufficient_tech_overlap_fails(sample_challenge, eligible_startup):
    startup = dict(eligible_startup)
    startup["technologies"] = ["Blockchain", "Web3"]  # 0 overlap with IoT/Sensors/Analytics
    
    result = check_eligibility(sample_challenge, startup, quote=800000, current_year=2026)
    assert result["eligible"] is False
    assert any("technology overlap" in r for r in result["failed_reasons"])
    assert result["eligibility_report"]["technology_overlap"]["passed"] is False


def test_quote_exceeding_budget_fails(sample_challenge, eligible_startup):
    result = check_eligibility(sample_challenge, eligible_startup, quote=1200000, current_year=2026)
    assert result["eligible"] is False
    assert any("Quote" in r for r in result["failed_reasons"])
    assert result["eligibility_report"]["budget_within_range"]["passed"] is False


def test_json_string_rules_handling():
    challenge = {
        "required_tech": '["IoT", "AI"]',
        "budget": 500000,
        "eligibility_rules": '{"registered_startup": true, "min_technology_overlap": 1}'
    }
    startup = {
        "dpiit_number": "DIPP9999",
        "technologies": '["IoT", "Cloud"]',
        "incorporation_year": 2022
    }
    result = check_eligibility(challenge, startup)
    assert result["eligible"] is True
    assert result["eligibility_report"]["technology_overlap"]["passed"] is True


def test_sqlmodel_object_compatibility():
    """Simulates real SQLModel class instances with _json column suffixes as in models.py."""
    class FakeChallengeModel:
        def __init__(self):
            self.id = 1
            self.title = "Clean Ganga Water Monitoring"
            self.budget = 750000
            self.required_tech = ["Sensors", "Telemetry"]
            self.eligibility_rules_json = {
                "registered_startup": True,
                "required_certification": "ISO 9001",
                "min_experience_years": 1,
                "min_technology_overlap": 1,
            }

    class FakeStartupModel:
        def __init__(self):
            self.id = 4
            self.name = "JalShuddh AI"
            self.dpiit_number = "DIPP62041"
            self.incorporation_year = 2021
            self.technologies = ["Sensors", "Spectroscopy", "Edge AI"]
            self.certifications = ["ISO 9001:2015", "NABL"]

    challenge = FakeChallengeModel()
    startup = FakeStartupModel()

    result = check_eligibility(challenge, startup, current_year=2026)
    assert result["eligible"] is True
    assert result["eligibility_report"]["registered_startup"]["passed"] is True
    assert result["eligibility_report"]["required_certification"]["passed"] is True
    assert result["eligibility_report"]["technology_overlap"]["passed"] is True

