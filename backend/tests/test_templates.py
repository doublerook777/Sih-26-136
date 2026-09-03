import os
import json
import jinja2
import pytest


@pytest.fixture
def jinja_env():
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "app", "templates")
    loader = jinja2.FileSystemLoader(templates_dir)
    return jinja2.Environment(loader=loader, autoescape=True)


def test_problem_statement_template_renders_all_15_sections(jinja_env):
    template = jinja_env.get_template("problem_statement.html")

    seed_challenges_file = os.path.join(os.path.dirname(__file__), "..", "seed_data", "challenges.json")
    with open(seed_challenges_file) as f:
        challenges = json.load(f)

    challenge = challenges[0]
    rendered = template.render(
        challenge=challenge,
        title=challenge["title"],
        department=challenge["department"],
        district=challenge["district"],
        sector=challenge["sector"],
        budget=challenge["budget"],
        timeline_days=challenge["timeline_days"],
        deadline=challenge["deadline"],
        statement=challenge["statement_json"],
        generated_at="2026-08-29",
    )

    assert "<!DOCTYPE html>" in rendered
    assert "Government Innovation & Public Procurement Portal" in rendered
    assert "Urban Water Supply" in rendered
    assert "District A" in rendered
    assert "Reduce Municipal Water Leakage" in rendered

    # All 15 standardized sections in order
    sections = [
        "1. Problem Definition",
        "2. Background & Administrative Context",
        "3. Existing System & Current Practices",
        "4. Identified Operational Gap",
        "5. Desired Innovation Solution",
        "6. Target Users & Stakeholders",
        "7. Technical Architecture & System Requirements",
        "8. Operational Constraints & Field Limitations",
        "9. Budget Allocation & Financial Framework",
        "10. Pilot Implementation Timeline & Phasing",
        "11. Expected Outcomes & Deliverables",
        "12. Key Performance Indicators (KPIs)",
        "13. Startup Eligibility Requirements",
        "14. Data Governance & Integration Requirements",
        "15. Cybersecurity & Compliance Requirements",
    ]

    for section in sections:
        assert section in rendered, f"Missing section: {section}"


def test_eligibility_criteria_template_renders(jinja_env):
    template = jinja_env.get_template("eligibility_criteria.html")

    seed_challenges_file = os.path.join(os.path.dirname(__file__), "..", "seed_data", "challenges.json")
    with open(seed_challenges_file) as f:
        challenges = json.load(f)

    challenge = challenges[0]
    rendered = template.render(
        challenge=challenge,
        title=challenge["title"],
        department=challenge["department"],
        district=challenge["district"],
        sector=challenge["sector"],
        budget=challenge["budget"],
        eligibility_rules=challenge["eligibility_rules_json"],
        generated_at="2026-08-29",
    )

    assert "Startup Eligibility & Mandatory Screening Gate Specification" in rendered
    assert "1. DPIIT Registration" in rendered
    assert "2. Required Certification" in rendered
    assert "3. Minimum Experience" in rendered
    assert "4. Technology Capability Overlap" in rendered
    assert "5. Budget & Commercial Ceiling" in rendered
    assert "ISO 9001:2015" in rendered


def test_evaluation_criteria_template_renders(jinja_env):
    template = jinja_env.get_template("evaluation_criteria.html")

    seed_challenges_file = os.path.join(os.path.dirname(__file__), "..", "seed_data", "challenges.json")
    with open(seed_challenges_file) as f:
        challenges = json.load(f)

    seed_rubrics_file = os.path.join(os.path.dirname(__file__), "..", "seed_data", "rubrics.json")
    with open(seed_rubrics_file) as f:
        rubrics = json.load(f)

    challenge = challenges[0]
    eval_rubric = next(r for r in rubrics if r["kind"] == "evaluation" and r["is_default"])

    rendered = template.render(
        challenge=challenge,
        title=challenge["title"],
        department=challenge["department"],
        district=challenge["district"],
        sector=challenge["sector"],
        rubric=eval_rubric,
        rubric_name=eval_rubric["name"],
        criteria=eval_rubric["criteria"],
        generated_at="2026-08-29",
    )

    assert "Expert Evaluation & Scoring Rubric Specification" in rendered
    assert "Default expert panel" in rendered
    assert "Technical Feasibility" in rendered or "technical_feasibility" in rendered
    assert "25%" in rendered
    assert "Innovation" in rendered or "innovation" in rendered
    assert "Cost Effectiveness" in rendered or "cost_effectiveness" in rendered
    assert "Scalability" in rendered or "scalability" in rendered
    assert "Security" in rendered or "security" in rendered
    assert "Implementation Capability" in rendered or "implementation_capability" in rendered
    assert "Social Impact" in rendered or "social_impact" in rendered
    assert "TOTAL ALLOCATED WEIGHT" in rendered
    assert "100%" in rendered

