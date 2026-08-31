"""
Problem Statement Generator for ProcuraAI (SIH 26136).
Produces the 15-section standardized problem statement required by the platform.
Supports Gemini AI generation with guaranteed template fallback.
"""
from typing import Any, Dict, Optional
from app.ai.client import generate_content


SECTIONS = [
    "problem",
    "background",
    "existing_system",
    "identified_gap",
    "desired_solution",
    "target_users",
    "technical_requirements",
    "constraints",
    "budget",
    "timeline",
    "expected_outcomes",
    "kpis",
    "eligibility_requirements",
    "data_requirements",
    "security_requirements",
]


def generate_template_statement(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic 15-section template fallback when LLM is offline or unavailable.
    """
    title = data.get("title") or "Public Sector Challenge"
    raw_desc = data.get("raw_description") or "Challenge description pending."
    dept = data.get("department") or "Concerned Department"
    district = data.get("district") or "Assigned District"
    sector = (data.get("sector") or "general").replace("_", " ").title()
    budget_val = data.get("budget")
    budget_str = f"INR {budget_val:,}" if budget_val else "As per government allocation and sanction limits."
    timeline_val = data.get("timeline_days")
    timeline_str = f"{timeline_val} days from work order issuance" if timeline_val else "90 to 180 days pilot duration."

    return {
        "problem": f"{title}: {raw_desc}",
        "background": f"Under the administration of {dept} in {district}, public service delivery in the {sector} sector requires modernization through agile startup innovation.",
        "existing_system": f"Current operations in {district} rely on manual inspections, periodic auditing, and legacy departmental workflows that lack real-time visibility.",
        "identified_gap": f"Lack of automated monitoring, predictive insights, and verified telemetry across {dept} operations, leading to delays and resource leakage.",
        "desired_solution": f"A scalable, startup-led technology intervention offering automated detection, real-time analytics, and open standard integration for {dept}.",
        "target_users": f"Field officers of {dept}, municipal administrators in {district}, and citizens benefiting from improved {sector} infrastructure.",
        "technical_requirements": "Modular cloud/edge architecture, RESTful API integrations, responsive dashboards, and automated telemetry logging.",
        "constraints": "Strict adherence to state IT procurement policies, compatibility with existing district infrastructure, and zero downtime deployment.",
        "budget": f"Estimated allocation: {budget_str}. Milestone-linked disbursement based on verified deliverable outcomes.",
        "timeline": f"Deployment and pilot evaluation schedule: {timeline_str}.",
        "expected_outcomes": f"Measurable improvement in operational efficiency, reduction in downtime, and structured compliance data for {dept}.",
        "kpis": "Target operational efficiency improvement >= 20%, error/leakage reduction >= 25%, 99.5% uptime during pilot phase.",
        "eligibility_requirements": "DPIIT-recognized startups with proven technology readiness (TRL 6+), relevant domain experience, and clean statutory compliance.",
        "data_requirements": "All operational data must reside within national sovereign boundaries and support encrypted data exports in standard JSON/CSV formats.",
        "security_requirements": "End-to-end encryption in transit (TLS 1.3) and at rest (AES-256), role-based access control (RBAC), and CERT-In compliance baseline.",
        "generated_by": "template",
    }


def generate_problem_statement(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates structured 15-section problem statement JSON using Gemini or fallback template.
    Guarantees exactly all 15 sections are returned with generated_by status.
    """
    title = data.get("title", "")
    raw_desc = data.get("raw_description", "")
    dept = data.get("department", "")
    district = data.get("district", "")
    sector = data.get("sector", "")
    budget = data.get("budget", "")
    timeline_days = data.get("timeline_days", "")

    prompt = f"""You are an expert government public procurement officer drafting a formal 15-section problem statement for an agile startup pilot challenge.

Challenge Details:
- Title: {title}
- Department: {dept}
- District: {district}
- Sector: {sector}
- Budget: INR {budget}
- Timeline: {timeline_days} days
- Raw Description: {raw_desc}

Generate a JSON object containing EXACTLY these 15 string keys:
1. "problem": concise problem definition
2. "background": institutional and sector background
3. "existing_system": baseline legacy system and current practices
4. "identified_gap": specific operational bottlenecks and unmet needs
5. "desired_solution": target startup solution overview
6. "target_users": stakeholders, officers, and beneficiaries
7. "technical_requirements": hardware/software/cloud specifications
8. "constraints": regulatory, environmental, and budgetary constraints
9. "budget": clear financial breakdown and disbursement conditions
10. "timeline": milestone schedule and deployment milestones
11. "expected_outcomes": qualitative and quantitative benefits
12. "kpis": specific measurable metrics and targets
13. "eligibility_requirements": mandatory startup qualification criteria
14. "data_requirements": data storage, privacy, and sovereignty terms
15. "security_requirements": cybersecurity, encryption, and audit compliance

Return ONLY a valid JSON object with all 15 keys populated with detailed, professional government procurement language.
"""

    system_instruction = "You are a government procurement drafting engine. Return strictly a JSON object with all 15 required sections."

    res = generate_content(
        prompt=prompt,
        system_instruction=system_instruction,
        response_mime_type="application/json",
        timeout_seconds=10,
    )

    if res.get("success") and res.get("json"):
        parsed = res["json"]
        if isinstance(parsed, dict) and all(k in parsed for k in SECTIONS):
            result = {k: str(parsed[k]) for k in SECTIONS}
            result["generated_by"] = "llm"
            return result

    # Fallback to deterministic template
    return generate_template_statement(data)
