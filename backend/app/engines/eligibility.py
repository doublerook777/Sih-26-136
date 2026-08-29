"""
Eligibility Screening Engine for ProcuraAI (SIH 26136).
Pure function executing 6 pass/fail gate checks before scoring.
Zero database imports, zero network calls.
"""
from typing import Any, Dict, Optional, Set


def check_eligibility(
    challenge: Dict[str, Any],
    startup: Dict[str, Any],
    quote: Optional[int] = None,
    current_year: int = 2026,
) -> Dict[str, Any]:
    """
    Evaluates a startup against a challenge's eligibility rules across 6 gates:
    1. registered_startup (DPIIT registration number check)
    2. required_certification (Certification check)
    3. min_experience_years (Operational experience years check)
    4. technology_overlap (Required tech vs startup capability tags)
    5. budget_within_range (Startup quote vs challenge budget)
    6. security_baseline (Cybersecurity baseline compliance)

    Returns:
        {
            "eligible": bool,
            "eligibility_report": {
                "registered_startup": {"passed": bool, "note": str},
                "required_certification": {"passed": bool, "note": str},
                "min_experience_years": {"passed": bool, "note": str},
                "technology_overlap": {"passed": bool, "note": str},
                "budget_within_range": {"passed": bool, "note": str},
                "security_baseline": {"passed": bool, "note": str},
            }
        }
    """
    rules = challenge.get("eligibility_rules_json") or challenge.get("eligibility_rules") or {}

    report: Dict[str, Dict[str, Any]] = {}

    # 1. Registered Startup Check (DPIIT)
    req_registration = rules.get("registered_startup", True)
    if req_registration:
        dpiit = startup.get("dpiit_number")
        if dpiit and str(dpiit).strip():
            report["registered_startup"] = {
                "passed": True,
                "note": str(dpiit).strip(),
            }
        else:
            report["registered_startup"] = {
                "passed": False,
                "note": "No DPIIT registration number found",
            }
    else:
        report["registered_startup"] = {
            "passed": True,
            "note": "Registration check waived",
        }

    # 2. Required Certification Check
    req_cert = rules.get("required_certification")
    if req_cert and str(req_cert).strip():
        cert_target = str(req_cert).strip().lower()
        startup_certs = [str(c).strip().lower() for c in startup.get("certifications", []) if c]
        matched_cert = any(
            cert_target == sc or cert_target in sc for sc in startup_certs
        )
        if matched_cert:
            report["required_certification"] = {
                "passed": True,
                "note": f"{req_cert} present",
            }
        else:
            report["required_certification"] = {
                "passed": False,
                "note": f"Missing required certification: {req_cert}",
            }
    else:
        report["required_certification"] = {
            "passed": True,
            "note": "No specific certification required",
        }

    # 3. Minimum Experience Years Check
    min_years = rules.get("min_experience_years", 0)
    inc_year = startup.get("incorporation_year")
    if inc_year and isinstance(inc_year, int) and inc_year <= current_year:
        experience_years = current_year - inc_year
    else:
        experience_years = 0

    if experience_years >= min_years:
        report["min_experience_years"] = {
            "passed": True,
            "note": f"{experience_years} years, needs {min_years}",
        }
    else:
        report["min_experience_years"] = {
            "passed": False,
            "note": f"{experience_years} years, needs {min_years}",
        }

    # 4. Technology Overlap Check (Scores against tech_tags)
    min_overlap = rules.get("min_technology_overlap", 1)
    req_tech = [str(t).strip().lower() for t in challenge.get("required_tech", []) if t]
    startup_tags = [str(t).strip().lower() for t in startup.get("tech_tags", []) if t]
    
    # Fallback to technologies list only if tech_tags is not present
    if not startup_tags and startup.get("technologies"):
        startup_tags = [str(t).strip().lower() for t in startup.get("technologies", []) if t]

    matched_tech = [rt for rt in req_tech if rt in startup_tags]
    overlap_count = len(matched_tech)
    total_req = len(req_tech)

    if overlap_count >= min_overlap:
        report["technology_overlap"] = {
            "passed": True,
            "note": f"{overlap_count} of {total_req} matched",
        }
    else:
        report["technology_overlap"] = {
            "passed": False,
            "note": f"{overlap_count} of {total_req} matched (requires at least {min_overlap})",
        }

    # 5. Budget Within Range Check
    budget = challenge.get("budget") or rules.get("max_quote")
    effective_quote = quote if quote is not None else startup.get("quote")

    if effective_quote is not None and budget is not None:
        quote_display = f"{effective_quote / 100000:.1f}L" if effective_quote >= 100000 else f"₹{effective_quote:,}"
        budget_display = f"{budget / 100000:.1f}L" if budget >= 100000 else f"₹{budget:,}"

        if effective_quote <= budget:
            report["budget_within_range"] = {
                "passed": True,
                "note": f"quote {quote_display} of {budget_display}",
            }
        else:
            report["budget_within_range"] = {
                "passed": False,
                "note": f"quote {quote_display} exceeds budget {budget_display}",
            }
    else:
        report["budget_within_range"] = {
            "passed": True,
            "note": "Within budget range",
        }

    # 6. Security Baseline Check
    req_sec = rules.get("security_baseline", True)
    if req_sec:
        sec_val = startup.get("security_baseline", True)
        if sec_val is not False:
            report["security_baseline"] = {
                "passed": True,
                "note": "self-declared",
            }
        else:
            report["security_baseline"] = {
                "passed": False,
                "note": "Security baseline not satisfied",
            }
    else:
        report["security_baseline"] = {
            "passed": True,
            "note": "No security baseline required",
        }

    # Overall eligibility: passes only if all 6 gates pass
    all_passed = all(gate["passed"] for gate in report.values())

    return {
        "eligible": all_passed,
        "eligibility_report": report,
        "report": report,  # alias for backwards compatibility
    }
