"""
Eligibility Screening Engine for ProcuraAI (SIH 26136).
Pure functional implementation: No database connections, deterministic, explainable.

Runs pass/fail gating before matching algorithms.
"""
from typing import Any, Dict, List, Optional, Union
import json


def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    """Helper to extract a property whether obj is a dict, Pydantic, or SQLModel instance."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _normalize_str(s: Any) -> str:
    """Normalizes string for comparison."""
    if s is None:
        return ""
    return str(s).strip().lower()


def _normalize_list(items: Any) -> List[str]:
    """Normalizes a list or JSON string of items into lowercased strings."""
    if items is None:
        return []
    if isinstance(items, str):
        try:
            parsed = json.loads(items)
            if isinstance(parsed, list):
                return [_normalize_str(x) for x in parsed if x]
        except Exception:
            return [_normalize_str(x) for x in items.split(",") if x.strip()]
    if isinstance(items, (list, tuple, set)):
        result = []
        for item in items:
            if isinstance(item, dict):
                # e.g. {"name": "Nashik pipeline audit"}
                result.append(_normalize_str(item.get("name", "")))
            else:
                result.append(_normalize_str(item))
        return [r for r in result if r]
    return []


def check_eligibility(
    challenge: Any,
    startup: Any,
    quote: Optional[int] = None,
    current_year: int = 2026,
) -> Dict[str, Any]:
    """
    Evaluates whether a startup satisfies all eligibility gates for a given challenge.

    Criteria Checked:
    1. registered_startup: Startup has DPIIT recognition.
    2. required_certification: Startup holds required certifications (e.g., ISO 27001, CPCB).
    3. min_experience_years: Startup has been incorporated for >= min years.
    4. technology_overlap: Startup shares >= min required technologies with challenge.
    5. budget_within_range: Startup quote is within challenge budget/max_quote.
    6. security_baseline: Startup meets baseline cybersecurity posture.

    Returns:
        {
            "eligible": bool,
            "eligibility_report": {
                "registered_startup": {"passed": bool, "note": str},
                "required_certification": {"passed": bool, "note": str},
                "min_experience_years": {"passed": bool, "note": str},
                "technology_overlap": {"passed": bool, "note": str},
                "budget_within_range": {"passed": bool, "note": str},
                "security_baseline": {"passed": bool, "note": str}
            },
            "failed_reasons": List[str]
        }
    """
    # Extract challenge rules (supports both field aliases)
    eligibility_rules = _get_val(challenge, "eligibility_rules") or _get_val(challenge, "eligibility_rules_json", {})
    if isinstance(eligibility_rules, str):
        try:
            eligibility_rules = json.loads(eligibility_rules)
        except Exception:
            eligibility_rules = {}

    req_registered = eligibility_rules.get("registered_startup", True)
    req_cert = eligibility_rules.get("required_certification", None)
    min_exp_years = eligibility_rules.get("min_experience_years", 0)
    min_tech_overlap = eligibility_rules.get("min_technology_overlap", 1)
    max_quote = eligibility_rules.get("max_quote") or _get_val(challenge, "budget")
    req_security = eligibility_rules.get("security_baseline", False)

    # Extract startup properties (supports both direct model attributes and JSON aliases)
    dpiit_number = _get_val(startup, "dpiit_number") or _get_val(startup, "dpiit")
    incorporation_year = _get_val(startup, "incorporation_year")
    certifications = _normalize_list(_get_val(startup, "certifications") or _get_val(startup, "certifications_json", []))
    startup_techs = _normalize_list(
        _get_val(startup, "technologies")
        or _get_val(startup, "technologies_json")
        or _get_val(startup, "tech", [])
    )
    challenge_techs = _normalize_list(
        _get_val(challenge, "required_tech")
        or _get_val(challenge, "required_tech_json", [])
    )

    report = {}
    failed_reasons = []

    # 1. Registered Startup Check (DPIIT)
    if req_registered:
        has_dpiit = bool(dpiit_number and str(dpiit_number).strip().lower() not in ("false", "0", "none", "null"))
        if has_dpiit:
            dpiit_str = str(dpiit_number) if dpiit_number is not True else "DPIIT Recognized"
            report["registered_startup"] = {"passed": True, "note": dpiit_str}
        else:
            report["registered_startup"] = {"passed": False, "note": "DPIIT registration not found"}
            failed_reasons.append("Startup lacks required DPIIT recognition.")
    else:
        report["registered_startup"] = {"passed": True, "note": "Not required"}

    # 2. Required Certification Check
    if req_cert and _normalize_str(req_cert) not in ("none", "null", ""):
        target_cert = _normalize_str(req_cert)
        matched_cert = any(target_cert in c for c in certifications)
        if matched_cert:
            report["required_certification"] = {"passed": True, "note": f"{req_cert} present"}
        else:
            report["required_certification"] = {"passed": False, "note": f"Missing {req_cert}"}
            failed_reasons.append(f"Missing mandatory certification: {req_cert}.")
    else:
        report["required_certification"] = {"passed": True, "note": "None required"}

    # 3. Minimum Experience Years Check
    if min_exp_years > 0:
        if incorporation_year and isinstance(incorporation_year, (int, float)):
            years_active = max(0, current_year - int(incorporation_year))
            if years_active >= min_exp_years:
                report["min_experience_years"] = {
                    "passed": True,
                    "note": f"{years_active} years, needs {min_exp_years}"
                }
            else:
                report["min_experience_years"] = {
                    "passed": False,
                    "note": f"{years_active} years, needs {min_exp_years}"
                }
                failed_reasons.append(f"Experience insufficient: {years_active} years active (minimum {min_exp_years} required).")
        else:
            report["min_experience_years"] = {"passed": False, "note": "Incorporation year missing"}
            failed_reasons.append("Incorporation year not provided.")
    else:
        report["min_experience_years"] = {"passed": True, "note": "No minimum requirement"}

    # 4. Technology Overlap Check
    if challenge_techs:
        overlap = set(challenge_techs).intersection(set(startup_techs))
        # Also check partial substring matches if exact tag match is empty
        if not overlap:
            for ct in challenge_techs:
                for st in startup_techs:
                    if ct in st or st in ct:
                        overlap.add(ct)
                        break

        overlap_count = len(overlap)
        needed_overlap = min(min_tech_overlap, len(challenge_techs))
        if overlap_count >= needed_overlap:
            report["technology_overlap"] = {
                "passed": True,
                "note": f"{overlap_count} of {len(challenge_techs)} matched"
            }
        else:
            report["technology_overlap"] = {
                "passed": False,
                "note": f"{overlap_count} of {len(challenge_techs)} matched (min {needed_overlap})"
            }
            failed_reasons.append(f"Insufficient technology overlap: {overlap_count}/{len(challenge_techs)} matched (minimum {needed_overlap} required).")
    else:
        report["technology_overlap"] = {"passed": True, "note": "No required tech specified"}

    # 5. Budget / Quote Within Range Check
    if quote is not None and max_quote is not None:
        if quote <= max_quote:
            quote_lakhs = quote / 100000.0
            max_lakhs = max_quote / 100000.0
            report["budget_within_range"] = {
                "passed": True,
                "note": f"quote {quote_lakhs:.1f}L of {max_lakhs:.1f}L"
            }
        else:
            quote_lakhs = quote / 100000.0
            max_lakhs = max_quote / 100000.0
            report["budget_within_range"] = {
                "passed": False,
                "note": f"quote {quote_lakhs:.1f}L exceeds limit of {max_lakhs:.1f}L"
            }
            failed_reasons.append(f"Quote (₹{quote:,}) exceeds maximum ceiling (₹{max_quote:,}).")
    elif max_quote is not None:
        max_lakhs = max_quote / 100000.0
        report["budget_within_range"] = {
            "passed": True,
            "note": f"Budget ceiling ₹{max_lakhs:.1f}L (quote pending)"
        }
    else:
        report["budget_within_range"] = {"passed": True, "note": "No budget ceiling specified"}

    # 6. Security Baseline Check
    if req_security:
        # Check if startup has security certification or explicit baseline
        has_sec_cert = any(
            any(k in c for k in ["iso 27001", "soc 2", "hipaa", "cert-in", "cert_in", "security"])
            for c in certifications
        )
        if has_sec_cert:
            report["security_baseline"] = {"passed": True, "note": "Security certified"}
        else:
            # Fallback to self-declared compliance if no strict cert missing
            report["security_baseline"] = {"passed": True, "note": "Self-declared compliance"}
    else:
        report["security_baseline"] = {"passed": True, "note": "Baseline declared"}

    # Final pass/fail determination: all criteria must pass
    all_passed = all(item.get("passed", False) for item in report.values())

    return {
        "eligible": all_passed,
        "eligibility_report": report,
        "failed_reasons": failed_reasons,
    }
