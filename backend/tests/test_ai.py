"""
Tests for Gemini AI Client and Problem Statement Generator (SIH 26136).
"""
import pytest
from app.ai.client import generate_content, test_gemini_connection as check_gemini_connection
from app.ai.problem_statement import generate_problem_statement, generate_template_statement, CANONICAL_SECTIONS


def test_generate_content_fallback_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    res = generate_content("Test prompt")
    assert res["success"] is False
    assert res["fallback"] is True
    assert "GEMINI_API_KEY" in res["error"]


def test_connection_helper_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    res = check_gemini_connection()
    assert res["connected"] is False
    assert "GEMINI_API_KEY" in res["message"]


def test_problem_statement_template_output_all_16_keys():
    statement = generate_template_statement(
        raw_description="Our municipal pipes leak silently underground.",
        title="Reduce Water Leakage",
        department="Urban Water Supply",
        district="District A",
        sector="water",
        budget=1000000,
        timeline_days=90,
    )

    assert len(statement) == 16
    for key in CANONICAL_SECTIONS:
        assert key in statement
        assert isinstance(statement[key], str)
        assert len(statement[key]) > 10
    assert statement["generated_by"] == "template"


def test_generate_problem_statement_fallback_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    statement = generate_problem_statement(
        raw_description="Our municipal pipes leak silently underground.",
        title="Reduce Water Leakage",
        department="Urban Water Supply",
        district="District A",
        sector="water",
        budget=1000000,
        timeline_days=90,
    )

    assert len(statement) == 16
    assert statement["generated_by"] == "template"
    for key in CANONICAL_SECTIONS:
        assert key in statement
        assert len(statement[key]) > 0


def test_generate_problem_statement_llm_path_with_mocked_gemini(monkeypatch):
    mock_llm_json = {
        "problem": "AI-Generated: Pipeline structural degradation and pressure loss.",
        "background": "AI-Generated: District A municipal network background.",
        "existing_system": "AI-Generated: Manual acoustic rod inspections.",
        "identified_gap": "AI-Generated: No real-time pressure sensing telemetry.",
        "desired_solution": "AI-Generated: IoT acoustic sensors with ML edge alerts.",
        "target_users": "AI-Generated: Field operators and district engineers.",
        "technical_requirements": "AI-Generated: LoRaWAN pressure transducers.",
        "constraints": "AI-Generated: Continuous municipal supply operations.",
        "budget": "AI-Generated: INR 10,00,000 all-inclusive.",
        "timeline": "AI-Generated: 90 days across 4 milestone phases.",
        "expected_outcomes": "AI-Generated: 35% reduction in NRW loss.",
        "kpis": "AI-Generated: Leak response < 6 hrs; uptime >= 98%.",
        "eligibility_requirements": "AI-Generated: DPIIT startup with ISO 9001.",
        "data_requirements": "AI-Generated: Encrypted time-series REST APIs.",
        "security_requirements": "AI-Generated: CERT-In compliance and AES-256.",
    }

    def mock_generate_content(*args, **kwargs):
        return {
            "success": True,
            "fallback": False,
            "json": mock_llm_json,
            "model": "mock-gemini",
        }

    monkeypatch.setattr("app.ai.problem_statement.generate_content", mock_generate_content)

    statement = generate_problem_statement(
        raw_description="Our pipes leak.",
        title="Water Leakage",
        department="Urban Water Supply",
        district="District A",
        sector="water",
    )

    assert len(statement) == 16
    assert statement["generated_by"] == "llm"
    for key in CANONICAL_SECTIONS:
        assert key in statement
        assert statement[key] == mock_llm_json[key]


def test_generate_problem_statement_missing_sections_filled_from_template(monkeypatch):
    # LLM returns JSON missing 3 sections: "constraints", "kpis", "security_requirements"
    partial_llm_json = {
        "problem": "AI-Generated Problem Statement",
        "background": "AI-Generated Background",
        "existing_system": "AI-Generated Existing System",
        "identified_gap": "AI-Generated Gap",
        "desired_solution": "AI-Generated Solution",
        "target_users": "AI-Generated Users",
        "technical_requirements": "AI-Generated Tech",
        "budget": "AI-Generated Budget",
        "timeline": "AI-Generated Timeline",
        "expected_outcomes": "AI-Generated Outcomes",
        "eligibility_requirements": "AI-Generated Eligibility",
        "data_requirements": "AI-Generated Data",
    }

    def mock_generate_content(*args, **kwargs):
        return {
            "success": True,
            "fallback": False,
            "json": partial_llm_json,
            "model": "mock-gemini",
        }

    monkeypatch.setattr("app.ai.problem_statement.generate_content", mock_generate_content)

    statement = generate_problem_statement(
        raw_description="Our pipes leak.",
        title="Water Leakage",
        department="Urban Water Supply",
        district="District A",
        sector="water",
    )

    # Exactly 16 keys returned
    assert len(statement) == 16
    assert statement["generated_by"] == "llm"

    # Present sections keep LLM output
    assert statement["problem"] == "AI-Generated Problem Statement"
    assert statement["desired_solution"] == "AI-Generated Solution"

    # Missing sections are filled from template
    assert len(statement["constraints"]) > 10
    assert len(statement["kpis"]) > 10
    assert len(statement["security_requirements"]) > 10
