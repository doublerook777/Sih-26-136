from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import Session, select

from app.auth import get_current_user
from app.db import get_session
from app.models import (
    Challenge,
    KPI,
    Milestone,
    Payment,
    Pilot,
    Procurement,
    Risk,
    Rubric,
    Startup,
    User,
    Validation,
)

router = APIRouter(prefix="/documents", tags=["documents"])

_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)

_DOCUMENTS = {
    "problem_statement": {
        "title": "Problem Statement",
        "description": "Standard 15-section challenge specification.",
        "entity": "challenge",
    },
    "eligibility_criteria": {
        "title": "Eligibility Criteria",
        "description": "Startup eligibility and mandatory screening requirements.",
        "entity": "challenge",
    },
    "evaluation_criteria": {
        "title": "Evaluation Criteria",
        "description": "Multi-criteria expert scoring rubric and weighting.",
        "entity": "challenge",
    },
    "pilot_agreement": {
        "title": "Pilot Agreement",
        "description": "16-clause agreement covering scope, IP, data, security and termination.",
        "entity": "pilot",
    },
    "milestone_contract": {
        "title": "Milestone Delivery Contract",
        "description": "Tranche-by-tranche milestone deliverables and verification criteria.",
        "entity": "pilot",
    },
    "data_ip": {
        "title": "Data Governance & IP Agreement",
        "description": "IP ownership, data privacy, and government data protection clauses.",
        "entity": "pilot",
    },
    "security_checklist": {
        "title": "Cybersecurity & Compliance Audit",
        "description": "8-point cybersecurity evaluation and verification matrix.",
        "entity": "pilot",
    },
    "risk_register": {
        "title": "Risk Management Register",
        "description": "Probability-impact risk matrix, scoring, and mitigation strategies.",
        "entity": "pilot",
    },
    "kpi_report": {
        "title": "KPI Report",
        "description": "Baseline, target, achieved, and attainment evidence.",
        "entity": "pilot",
    },
    "procurement_recommendation": {
        "title": "Procurement Recommendation",
        "description": "Evidence-backed procurement pathway.",
        "entity": "pilot",
    },
    "scale_up_decision": {
        "title": "Scale-up Decision",
        "description": "Final score and scale-up outcome.",
        "entity": "pilot",
    },
    "validation_report": {
        "title": "Validation Report",
        "description": "Independent milestone validation record.",
        "entity": "milestone",
    },
    "payment_approval": {
        "title": "Payment Approval",
        "description": "Validated milestone payment authorization.",
        "entity": "milestone",
    },
}


@router.get("/templates")
def list_document_templates(current_user: User = Depends(get_current_user)):
    return [
        {"doc_type": doc_type, **details}
        for doc_type, details in _DOCUMENTS.items()
    ]


@router.get("/{doc_type}/{entity_id}", response_class=HTMLResponse)
def render_document(
    doc_type: str,
    entity_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if doc_type not in _DOCUMENTS:
        raise HTTPException(status_code=404, detail=f"Document type '{doc_type}' is not available")

    doc_info = _DOCUMENTS[doc_type]
    entity_kind = doc_info.get("entity", "challenge")

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if entity_kind == "challenge" or doc_type in ["problem_statement", "eligibility_criteria", "evaluation_criteria"]:
        challenge = session.get(Challenge, entity_id)
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")

        eval_rubric = session.get(Rubric, challenge.evaluation_rubric_id) if challenge.evaluation_rubric_id else None
        match_rubric = session.get(Rubric, challenge.match_rubric_id) if challenge.match_rubric_id else None

        template = _env.get_template(f"{doc_type}.html")
        return HTMLResponse(
            content=template.render(
                challenge=challenge,
                challenge_id=challenge.id,
                entity_id=challenge.id,
                doc_type=doc_type,
                title=challenge.title,
                department=challenge.department,
                district=challenge.district,
                sector=challenge.sector,
                budget=challenge.budget,
                timeline_days=challenge.timeline_days,
                deadline=challenge.deadline,
                statement=challenge.statement_json,
                eligibility_rules=challenge.eligibility_rules_json,
                evaluation_rubric=eval_rubric,
                match_rubric=match_rubric,
                rubric=eval_rubric or match_rubric,
                generated_at=now_str,
            )
        )

    elif entity_kind == "pilot" or doc_type in ["pilot_agreement", "milestone_contract", "data_ip", "security_checklist", "risk_register"]:
        pilot = session.get(Pilot, entity_id)
        if not pilot:
            raise HTTPException(status_code=404, detail="Pilot not found")

        challenge = session.get(Challenge, pilot.challenge_id)
        startup = session.get(Startup, pilot.startup_id)
        milestones = session.exec(select(Milestone).where(Milestone.pilot_id == pilot.id).order_by(Milestone.seq)).all()
        kpis = session.exec(select(KPI).where(KPI.pilot_id == pilot.id)).all()
        risks = session.exec(select(Risk).where(Risk.pilot_id == pilot.id)).all()
        procurement = session.exec(select(Procurement).where(Procurement.pilot_id == pilot.id)).first()

        template = _env.get_template(f"{doc_type}.html")
        return HTMLResponse(
            content=template.render(
                pilot=pilot,
                challenge=challenge,
                startup=startup,
                milestones=milestones,
                kpis=kpis,
                risks=risks,
                security_checklist=pilot.security_checklist_json or {},
                decision=procurement.decision if procurement else None,
                final_score=procurement.final_score if procurement else None,
                justification=procurement.justification if procurement else None,
                title=challenge.title if challenge else "Innovation Pilot",
                department=challenge.department if challenge else "Department",
                district=pilot.location,
                generated_at=now_str,
            )
        )

    elif entity_kind == "milestone" or doc_type in ["validation_report", "payment_approval"]:
        milestone = session.get(Milestone, entity_id)
        if not milestone:
            raise HTTPException(status_code=404, detail="Milestone not found")

        pilot = session.get(Pilot, milestone.pilot_id)
        challenge = session.get(Challenge, pilot.challenge_id) if pilot else None
        startup = session.get(Startup, pilot.startup_id) if pilot else None
        validation = session.exec(
            select(Validation).where(Validation.milestone_id == milestone.id).order_by(Validation.validated_at.desc())
        ).first()
        payment = session.exec(select(Payment).where(Payment.milestone_id == milestone.id)).first()

        validation_dict = None
        validator_name = None
        if validation:
            validator = session.get(User, validation.validator_id)
            validator_name = validator.name if validator else None
            validation_dict = {
                "verdict": validation.verdict,
                "claimed_value": validation.claimed_value,
                "verified_value": validation.verified_value,
                "notes": validation.evidence_notes,
                "validator_name": validator_name,
                "validated_at": validation.validated_at,
            }

        template = _env.get_template(f"{doc_type}.html")
        return HTMLResponse(
            content=template.render(
                milestone=milestone,
                pilot=pilot,
                challenge=challenge,
                startup=startup,
                validation=validation_dict,
                validator_name=validator_name,
                payment=payment,
                title=challenge.title if challenge else "Innovation Pilot",
                department=challenge.department if challenge else "Department",
                district=pilot.location if pilot else None,
                generated_at=now_str,
            )
        )

    raise HTTPException(status_code=404, detail=f"Document handler for '{doc_type}' not found")
