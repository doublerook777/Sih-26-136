"""
Documents router for ProcuraAI (SIH 26136).
Renders printable Jinja2 HTML templates for challenges, pilots, and milestones.
Provides catalog of standard procurement document templates.
"""
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
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
    Startup,
    User,
    Validation,
)

router = APIRouter(prefix="/documents", tags=["documents"])

# Configure Jinja2 Template Environment
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)

CHALLENGE_DOC_TYPES = {
    "problem_statement",
    "eligibility_criteria",
    "evaluation_criteria",
}

PILOT_DOC_TYPES = {
    "pilot_agreement",
    "milestone_contract",
    "data_ip",
    "security_checklist",
    "risk_register",
    "kpi_report",
    "procurement_recommendation",
    "scale_up_decision",
}

MILESTONE_DOC_TYPES = {
    "validation_report",
    "payment_approval",
}

ALL_DOC_TYPES = CHALLENGE_DOC_TYPES | PILOT_DOC_TYPES | MILESTONE_DOC_TYPES

TEMPLATES_CATALOG = [
    {
        "doc_type": "problem_statement",
        "title": "Problem Statement",
        "description": "15-section structured challenge specification.",
        "entity": "challenge",
    },
    {
        "doc_type": "eligibility_criteria",
        "title": "Eligibility Criteria",
        "description": "Startup eligibility rules and mandatory compliance checklist.",
        "entity": "challenge",
    },
    {
        "doc_type": "evaluation_criteria",
        "title": "Evaluation Criteria",
        "description": "Expert scoring criteria and rubric weights breakdown.",
        "entity": "challenge",
    },
    {
        "doc_type": "pilot_agreement",
        "title": "Pilot Agreement",
        "description": "16-clause agreement covering scope, IP, data, security and termination.",
        "entity": "pilot",
    },
    {
        "doc_type": "milestone_contract",
        "title": "Milestone Contract",
        "description": "Milestone deliverables, payment schedules, and performance targets.",
        "entity": "pilot",
    },
    {
        "doc_type": "data_ip",
        "title": "Data & IP Governance",
        "description": "Data protection, confidentiality, and IP ownership terms.",
        "entity": "pilot",
    },
    {
        "doc_type": "security_checklist",
        "title": "Security Checklist",
        "description": "Cybersecurity compliance and vulnerability assessment report.",
        "entity": "pilot",
    },
    {
        "doc_type": "risk_register",
        "title": "Risk Register",
        "description": "Risk matrix, mitigation strategies, and probability-impact scoring.",
        "entity": "pilot",
    },
    {
        "doc_type": "kpi_report",
        "title": "KPI Performance Report",
        "description": "Baseline vs target vs achieved performance metrics across categories.",
        "entity": "pilot",
    },
    {
        "doc_type": "validation_report",
        "title": "Milestone Validation Report",
        "description": "Independent third-party verification report with claimed vs verified metrics.",
        "entity": "milestone",
    },
    {
        "doc_type": "payment_approval",
        "title": "Payment Approval Order",
        "description": "Treasury release authorization and milestone disbursement approval.",
        "entity": "milestone",
    },
    {
        "doc_type": "procurement_recommendation",
        "title": "Procurement Recommendation",
        "description": "Post-pilot evaluation, scoring rollup, and adoption pathway justification.",
        "entity": "pilot",
    },
    {
        "doc_type": "scale_up_decision",
        "title": "Scale-Up & Replication Order",
        "description": "Formal government scale-up sanction and district replication roadmap.",
        "entity": "pilot",
    },
]


@router.get("/templates")
def get_document_templates(
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, str]]:
    """Returns the catalog of all standard procurement document templates."""
    return TEMPLATES_CATALOG


@router.get("/{doc_type}/{entity_id}", response_class=HTMLResponse)
def render_document(
    doc_type: str,
    entity_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Renders any standard procurement Jinja2 template by document type and entity ID.
    Returns printable HTML (Content-Type: text/html).
    """
    if doc_type not in ALL_DOC_TYPES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown document type: '{doc_type}'",
        )

    context: Dict[str, Any] = {
        "doc_type": doc_type,
        "entity_id": entity_id,
        "current_user": current_user,
        "generated_at": datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC"),
    }

    if doc_type in CHALLENGE_DOC_TYPES:
        challenge = session.get(Challenge, entity_id)
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found",
            )
        context["challenge"] = challenge
        context["title"] = f"{doc_type.replace('_', ' ').title()} — {challenge.title}"

    elif doc_type in PILOT_DOC_TYPES:
        pilot = session.get(Pilot, entity_id)
        if not pilot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pilot not found",
            )
        challenge = session.get(Challenge, pilot.challenge_id)
        startup = session.get(Startup, pilot.startup_id)
        milestones = session.exec(
            select(Milestone).where(Milestone.pilot_id == entity_id).order_by(Milestone.seq)
        ).all()
        kpis = session.exec(
            select(KPI).where(KPI.pilot_id == entity_id)
        ).all()
        risks = session.exec(
            select(Risk).where(Risk.pilot_id == entity_id)
        ).all()
        procurement = session.exec(
            select(Procurement).where(Procurement.pilot_id == entity_id)
        ).first()

        context["pilot"] = pilot
        context["challenge"] = challenge
        context["startup"] = startup
        context["milestones"] = milestones
        context["kpis"] = kpis
        context["risks"] = risks
        context["procurement"] = procurement
        context["title"] = f"{doc_type.replace('_', ' ').title()} — Pilot #{pilot.id}"

    elif doc_type in MILESTONE_DOC_TYPES:
        milestone = session.get(Milestone, entity_id)
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found",
            )
        pilot = session.get(Pilot, milestone.pilot_id)
        challenge = session.get(Challenge, pilot.challenge_id) if pilot else None
        startup = session.get(Startup, pilot.startup_id) if pilot else None
        validation = session.exec(
            select(Validation).where(Validation.milestone_id == entity_id)
        ).first()
        payment = session.exec(
            select(Payment).where(Payment.milestone_id == entity_id)
        ).first()

        context["milestone"] = milestone
        context["pilot"] = pilot
        context["challenge"] = challenge
        context["startup"] = startup
        context["validation"] = validation
        context["payment"] = payment
        context["title"] = f"{doc_type.replace('_', ' ').title()} — Milestone #{milestone.id}"

    template_file = f"{doc_type}.html"
    try:
        template = jinja_env.get_template(template_file)
        rendered_content = template.render(**context)
        return HTMLResponse(content=rendered_content, status_code=200)
    except Exception as e:
        # Fallback to base template rendering if specific template fails
        base_template = jinja_env.get_template("base.html")
        fallback_content = base_template.render(**context)
        return HTMLResponse(content=fallback_content, status_code=200)
