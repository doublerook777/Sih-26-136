"""
Problem Statement Generator for ProcuraAI (SIH 26136).
Transforms an officer's rough input into a standardized 15-section Indian Public Procurement statement.
Supports both LLM generation via Gemini and deterministic fallback generation.
"""
import json
import logging
from typing import Any, Dict, Optional

from app.ai.client import generate_content

logger = logging.getLogger(__name__)

# The 15 canonical section keys plus generated_by
CANONICAL_SECTIONS = [
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


def _format_inr(amount: Optional[int]) -> str:
    if amount is None:
        return "INR 10,00,000"
    if amount >= 10000000:
        return f"₹{amount / 10000000:.2f} Cr"
    if amount >= 100000:
        return f"₹{amount / 100000:.1f} Lakhs"
    return f"₹{amount:,}"


def generate_template_statement(
    raw_description: str,
    title: str = "",
    department: str = "",
    district: str = "",
    sector: str = "",
    budget: Optional[int] = None,
    timeline_days: Optional[int] = None,
) -> Dict[str, str]:
    """
    Deterministic template generator that fills all 15 sections without any network call.
    Produces high-quality, readable public procurement specifications.
    """
    clean_desc = (raw_description or "").strip()
    clean_title = (title or "").strip() or "Public Innovation Challenge"
    clean_dept = (department or "").strip() or "Competent Municipal Authority"
    clean_dist = (district or "").strip() or "District Administration"
    clean_sec = (sector or "").strip().lower() or "public-services"
    sec_display = clean_sec.replace("_", " ").replace("-", " ").title()
    budget_display = _format_inr(budget) if budget else "INR 10,00,000"
    days = timeline_days or 90

    sector_templates = {
        "water": {
            "existing": "Manual physical inspections and reactive maintenance triggered by citizen complaints or surface flooding.",
            "gap": "Lack of continuous acoustic/pressure telemetry, leading to undetected underground non-revenue water (NRW) loss.",
            "solution": "Deploy IoT sensor nodes with edge telemetry and ML-driven leak detection algorithms for real-time anomaly alerting.",
            "tech": "Battery-operated pressure/acoustic sensors, LoRaWAN/cellular telemetry, GIS map dashboard, open REST APIs.",
            "outcomes": "Reduction of non-revenue water loss by at least 30% and under 6-hour leak localization across pilot distribution zones.",
            "kpis": "Leak detection time < 6 hrs; water wastage <= 20%; telemetry uptime >= 95%; cost per km <= ₹25,000.",
        },
        "healthcare": {
            "existing": "Paper-based patient token counters and manual triage recording across hospital registration wings.",
            "gap": "Severe OPD bottlenecking, unmanaged patient crowding, and absence of automated emergency triage classification.",
            "solution": "AI-powered queue management, automated patient triage classification, and real-time digital display slot integration.",
            "tech": "Cloud-native queue microservices, SMS/WhatsApp integration, kiosk touch interfaces, and HL7/FHIR compliance.",
            "outcomes": "Reduction in average OPD waiting time from >120 minutes to <45 minutes with prioritized emergency routing.",
            "kpis": "Average OPD wait time <= 45 mins; triage classification accuracy >= 90%; throughput >= 500 patients/day.",
        },
        "waste": {
            "existing": "Fixed schedule garbage truck routing with no visibility into bin fill levels or route deviations.",
            "gap": "Overflowing public waste receptacles, irregular collection frequency, and inefficient fuel utilization.",
            "solution": "Ultrasonic smart bin sensors coupled with dynamic AI vehicle route optimization and GIS tracking.",
            "tech": "Ultrasonic depth sensors, GPS fleet telematics, dynamic vehicle routing engine, and municipal admin portal.",
            "outcomes": "Elimination of overflowing bin incidents, 20% reduction in fleet fuel consumption, and verifiable SLA tracking.",
            "kpis": "Bin overflow incidents <= 2/month; route collection efficiency >= 90%; fuel cost reduction >= 18%.",
        },
        "transport": {
            "existing": "Static signal timing plans and manual traffic warden deployment at critical intersections.",
            "gap": "Inability to adapt signal timings to dynamic traffic surges, leading to peak-hour gridlock and emergency vehicle delays.",
            "solution": "Computer vision and radar-based adaptive traffic signal controllers with emergency corridor preemption.",
            "tech": "Edge AI video analytics, IP traffic cameras, adaptive SCATS/SCOOT controller interfaces, and central TMC feed.",
            "outcomes": "25% reduction in peak-hour intersection transit delays and guaranteed green-wave corridors for emergency vehicles.",
            "kpis": "Average intersection delay <= 90s; emergency preemption response < 5s; controller uptime >= 99%.",
        },
    }

    sec_info = sector_templates.get(clean_sec, {
        "existing": "Manual, periodic administrative reporting and traditional decentralized service delivery.",
        "gap": "Absence of real-time operational telemetry, predictive data analytics, and digital oversight.",
        "solution": "An outcome-focused technology pilot leveraging IoT, AI, or digital workflow optimization.",
        "tech": "Cloud-hosted microservices, secure RESTful APIs, role-based dashboards, and field data interfaces.",
        "outcomes": "Measurable enhancement in operational responsiveness, service delivery turnaround, and audit transparency.",
        "kpis": "Service turnaround reduction >= 30%; system reliability >= 95%; operational efficiency gain >= 20%.",
    })

    return {
        "problem": f"High operational bottleneck in {sec_display}: {clean_desc}",
        "background": (
            f"{clean_dept} in {clean_dist} requires a validated, outcome-oriented innovation pilot "
            f"in the {sec_display} sector to modernize administrative workflows and public service quality."
        ),
        "existing_system": sec_info["existing"],
        "identified_gap": sec_info["gap"],
        "desired_solution": (
            f"{sec_info['solution']} The solution must address: '{clean_desc}' with measurable pilot milestones."
        ),
        "target_users": (
            f"Department officers and field engineers of {clean_dept}, municipal administrators, and citizens of {clean_dist}."
        ),
        "technical_requirements": sec_info["tech"],
        "constraints": (
            f"The pilot implementation must strictly adhere to the {budget_display} financial ceiling "
            f"and complete within {days} calendar days without disrupting ongoing public operations."
        ),
        "budget": f"{budget_display} all-inclusive for hardware, cloud infrastructure, and {days}-day pilot validation.",
        "timeline": f"{days} calendar days across phased, milestone-based deliveries.",
        "expected_outcomes": sec_info["outcomes"],
        "kpis": sec_info["kpis"],
        "eligibility_requirements": (
            f"DPIIT-recognized startups with proven technology readiness (TRL 6+), relevant domain experience, "
            f"and compliance with published municipal procurement eligibility criteria."
        ),
        "data_requirements": (
            "All operational time-series data and audit logs must remain securely stored within India, "
            "exportable in standard CSV/JSON formats, and integrated with municipal dashboards."
        ),
        "security_requirements": (
            "Role-based access control (RBAC), end-to-end TLS 1.3 encryption in transit, AES-256 at rest, "
            "and compliance with CERT-In cybersecurity guidelines."
        ),
        "generated_by": "template",
    }


def generate_problem_statement(
    raw_description: Optional[str] = None,
    title: str = "",
    department: str = "",
    district: str = "",
    sector: str = "",
    budget: Optional[int] = None,
    timeline_days: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Transforms an officer's raw description into a standardized 15-section problem statement.
    Attempts generation via Gemini LLM; falls back cleanly to deterministic template generation
    on API failure, timeout, unparseable output, or missing keys.

    Always returns a dict with all 16 canonical keys, never raising an unhandled exception.
    """
    # Normalize inputs whether passed as named arguments or within kwargs/dict
    if isinstance(raw_description, dict):
        d = raw_description
        raw_desc = d.get("raw_description", "")
        t = d.get("title", title)
        dept = d.get("department", department)
        dist = d.get("district", district)
        sec = d.get("sector", sector)
        bud = d.get("budget", budget)
        t_days = d.get("timeline_days", timeline_days)
    else:
        raw_desc = raw_description or kwargs.get("raw_description", "")
        t = title or kwargs.get("title", "")
        dept = department or kwargs.get("department", "")
        dist = district or kwargs.get("district", "")
        sec = sector or kwargs.get("sector", "")
        bud = budget if budget is not None else kwargs.get("budget")
        t_days = timeline_days if timeline_days is not None else kwargs.get("timeline_days")

    # Generate baseline template output
    template_statement = generate_template_statement(
        raw_description=raw_desc,
        title=t,
        department=dept,
        district=dist,
        sector=sec,
        budget=bud,
        timeline_days=t_days,
    )

    bud_str = f"₹{bud:,}" if isinstance(bud, int) else "₹10,00,000"

    prompt = f"""You are an expert Indian Public Procurement and Smart City Problem Statement Drafting Assistant for ProcuraAI.
Your task is to transform a government officer's raw problem description into a highly structured, professional 15-section public procurement pilot problem statement.

INPUT DETAILS:
- Title: {t or 'Public Sector Challenge'}
- Raw Description: {raw_desc}
- Department: {dept or 'Municipal Administration'}
- District: {dist or 'District A'}
- Sector: {sec or 'Civic Services'}
- Budget Ceiling: {bud_str}
- Timeline: {t_days or 90} calendar days

INSTRUCTIONS:
Generate a JSON object containing EXACTLY the following 15 string keys:
1. "problem": Concise, formal problem summary.
2. "background": Administrative context and geographic background.
3. "existing_system": Description of traditional/manual practices currently used.
4. "identified_gap": Specific technological and operational bottleneck.
5. "desired_solution": Startup-led innovation requirements for pilot validation.
6. "target_users": Primary administrative and citizen user groups.
7. "technical_requirements": Architectural and technical specifications.
8. "constraints": Operational, regulatory, and integration constraints.
9. "budget": Budget breakdown and milestone allocation phrasing.
10. "timeline": Calendar phasing and milestone durations.
11. "expected_outcomes": Measurable benefits and service quality improvements.
12. "kpis": Concrete performance indicators with target values.
13. "eligibility_requirements": Startup criteria (DPIIT, experience, certifications).
14. "data_requirements": Data governance, storage, export, and API requirements.
15. "security_requirements": Cybersecurity, encryption, RBAC, and CERT-In compliance.

Respond ONLY with valid JSON. Do not include markdown fences, preambles, or additional commentary."""

    try:
        res = generate_content(
            prompt=prompt,
            response_mime_type="application/json",
            timeout_seconds=10,
        )

        if res.get("success") and res.get("json") and isinstance(res["json"], dict):
            llm_json = res["json"]
            final_output: Dict[str, Any] = {}

            # Populate each canonical section, falling back to template if missing or empty
            for key in CANONICAL_SECTIONS:
                val = llm_json.get(key)
                if val and isinstance(val, str) and val.strip():
                    final_output[key] = val.strip()
                else:
                    final_output[key] = template_statement[key]

            final_output["generated_by"] = "llm"
            return final_output

    except Exception as e:
        logger.warning(f"LLM statement generation failed ({e}), falling back to deterministic template.")

    # Complete fallback to template statement
    return template_statement
