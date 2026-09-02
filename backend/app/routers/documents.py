from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import Session

from app.auth import get_current_user
from app.db import get_session
from app.models import Challenge, User

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

    challenge = session.get(Challenge, entity_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

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
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        )
    )
