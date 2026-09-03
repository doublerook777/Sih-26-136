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


def test_pilot_agreement_template_renders_all_16_clauses(jinja_env):
    template = jinja_env.get_template("pilot_agreement.html")

    pilot = {
        "id": 1,
        "challenge_id": 1,
        "challenge_title": "Reduce municipal water leakage",
        "startup_id": 3,
        "startup_name": "AquaSense Systems",
        "location": "District A",
        "duration_days": 90,
        "budget": 1000000,
        "department": "Urban Water Supply",
    }
    challenge = {
        "id": 1,
        "title": "Reduce municipal water leakage",
        "department": "Urban Water Supply",
        "district": "District A",
        "budget": 1000000,
    }
    startup = {"id": 3, "name": "AquaSense Systems"}
    milestones = [
        {"seq": 1, "title": "Prototype", "deliverable": "40-node sensor prototype", "amount": 200000, "due_date": "2026-09-20"},
        {"seq": 2, "title": "Field trial", "deliverable": "Live data for 2 weeks", "amount": 300000, "due_date": "2026-10-10"},
        {"seq": 3, "title": "Deployment", "deliverable": "Full district coverage", "amount": 300000, "due_date": "2026-11-01"},
        {"seq": 4, "title": "Final results", "deliverable": "Verified KPI report", "amount": 200000, "due_date": "2026-11-25"},
    ]

    rendered = template.render(
        pilot=pilot,
        challenge=challenge,
        startup=startup,
        milestones=milestones,
        generated_at="2026-09-01",
    )

    assert "Innovation Pilot Implementation Agreement" in rendered
    assert "AquaSense Systems" in rendered
    assert "1,000,000" in rendered
    assert "M1" in rendered and "M2" in rendered and "M3" in rendered and "M4" in rendered
    assert "200,000" in rendered and "300,000" in rendered

    # All 16 clauses present
    for i in range(1, 17):
        assert f"Clause {i}:" in rendered, f"Missing Clause {i}"


def test_data_ip_template_renders(jinja_env):
    template = jinja_env.get_template("data_ip.html")

    pilot = {
        "id": 1,
        "challenge_title": "Reduce municipal water leakage",
        "startup_name": "AquaSense Systems",
        "location": "District A",
        "department": "Urban Water Supply",
    }
    challenge = {"id": 1, "title": "Reduce municipal water leakage", "department": "Urban Water Supply"}
    startup = {"id": 3, "name": "AquaSense Systems"}

    rendered = template.render(pilot=pilot, challenge=challenge, startup=startup)

    assert "Data Ownership & Intellectual Property Governance Terms" in rendered
    assert "Pre-Existing Background Intellectual Property" in rendered
    assert "Sovereign Ownership of Municipal & Public Data" in rendered
    assert "Pilot-Developed Foreground Intellectual Property" in rendered
    assert "Commercialization & National Replication Framework" in rendered


def test_security_checklist_template_renders(jinja_env):
    template = jinja_env.get_template("security_checklist.html")

    pilot = {"id": 1, "startup_name": "AquaSense Systems", "location": "District A"}
    challenge = {"id": 1, "title": "Reduce municipal water leakage", "department": "Urban Water Supply"}
    startup = {"id": 3, "name": "AquaSense Systems"}
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

    rendered = template.render(
        pilot=pilot,
        challenge=challenge,
        startup=startup,
        security_checklist=checklist,
        security_status="needs_remediation",
        score=87.5,
    )

    assert "8-Point Cybersecurity Baseline Audit Report" in rendered
    assert "NEEDS REMEDIATION" in rendered
    assert "87.5%" in rendered
    assert "Authentication" in rendered
    assert "Incident Response Plan" in rendered


def test_risk_register_template_renders(jinja_env):
    template = jinja_env.get_template("risk_register.html")

    pilot = {"id": 1, "startup_name": "AquaSense Systems", "location": "District A", "risk_level": "medium"}
    challenge = {"id": 1, "title": "Reduce municipal water leakage", "department": "Urban Water Supply"}
    startup = {"id": 3, "name": "AquaSense Systems"}
    risks = [
        {"description": "Sensor failure in monsoon", "probability": 3, "impact": 4, "score": 12, "mitigation": "Ship 10% spare nodes", "owner": "AquaSense"},
        {"description": "Cellular blind spots", "probability": 2, "impact": 3, "score": 6, "mitigation": "Deploy LoRaWAN relay", "owner": "AquaSense"},
    ]

    rendered = template.render(
        pilot=pilot,
        challenge=challenge,
        startup=startup,
        risks=risks,
        risk_level="medium",
    )

    assert "Pilot Risk Register & Governance Matrix" in rendered
    assert "MEDIUM" in rendered
    assert "Sensor failure in monsoon" in rendered
    assert "Ship 10% spare nodes" in rendered
    assert "12" in rendered


