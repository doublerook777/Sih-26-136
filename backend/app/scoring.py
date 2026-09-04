"""
Router-side glue between the ORM and the pure engines in app/engines/.
Not itself an engine: it may import models, since its whole job is turning
ORM rows into the plain dicts eligibility.py and matching.py expect.
"""
from typing import Any, Dict, Optional

from sqlmodel import Session, select

from app.engines.eligibility import check_eligibility
from app.engines.matching import score_match
from app.models import Challenge, Rubric, Startup


def resolve_rubric(session: Session, rubric_id: Optional[int], kind: str) -> Optional[Rubric]:
    """
    Loads the rubric a challenge points to, falling back to the active default
    for `kind` when the challenge has no rubric set (docs/SCHEMA.md: the two
    rubric FKs on Challenge are nullable for exactly this reason).
    """
    if rubric_id is not None:
        rubric = session.get(Rubric, rubric_id)
        if rubric is not None:
            return rubric
    return session.exec(
        select(Rubric).where(Rubric.kind == kind, Rubric.is_default == True)  # noqa: E712
    ).first()


def challenge_to_dict(challenge: Challenge) -> Dict[str, Any]:
    return {
        "sector": challenge.sector,
        "required_tech": challenge.required_tech,
        "budget": challenge.budget,
        "eligibility_rules_json": challenge.eligibility_rules_json,
    }


def startup_to_dict(startup: Startup) -> Dict[str, Any]:
    return {
        "name": startup.name,
        "sector": startup.sector,
        "tech_tags": startup.tech_tags,
        "technologies": startup.technologies,
        "dpiit_number": startup.dpiit_number,
        "incorporation_year": startup.incorporation_year,
        "team_size": startup.team_size,
        "past_projects": startup.past_projects,
        "certifications": startup.certifications,
    }


def score_application(
    challenge: Challenge,
    startup: Startup,
    weights: Dict[str, float],
    quote: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Runs the eligibility gate then the match engine for one challenge/startup
    pair, and applies the contract's rule that an ineligible startup always
    scores 0 (docs/API.md section 5), even if individual factors would have
    scored above zero.
    """
    challenge_dict = challenge_to_dict(challenge)
    startup_dict = startup_to_dict(startup)

    eligibility_result = check_eligibility(challenge_dict, startup_dict, quote=quote)
    match_result = score_match(
        challenge_dict,
        startup_dict,
        weights,
        eligibility=eligibility_result,
        quote=quote,
    )

    eligible = eligibility_result["eligible"]
    if not eligible:
        match_result = {
            **match_result,
            "match_score": 0.0,
            "match_breakdown": {key: 0.0 for key in match_result["match_breakdown"]},
        }

    return {
        "eligible": eligible,
        "eligibility_report": eligibility_result["eligibility_report"],
        "match_score": match_result["match_score"],
        "match_breakdown": match_result["match_breakdown"],
        "rubric_snapshot": match_result["rubric_snapshot"],
        "explanation": match_result["explanation"],
    }
