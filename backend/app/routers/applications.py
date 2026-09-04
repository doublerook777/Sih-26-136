from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_user, require_role
from app.db import get_session
from app.models import Application, Challenge, Startup, User
from app.schemas import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationSelectOut,
    ApplicationShortlistOut,
)
from app.scoring import resolve_rubric, score_application

router = APIRouter(tags=["applications"])


def _application_read(session: Session, application: Application) -> ApplicationRead:
    startup = session.get(Startup, application.startup_id)
    return ApplicationRead(
        application_id=application.id,
        startup_id=application.startup_id,
        startup_name=startup.name if startup else "Unknown startup",
        eligible=application.eligible,
        eligibility_report=application.eligibility_report_json,
        match_score=application.match_score,
        match_breakdown=application.match_breakdown_json,
        rubric_snapshot=application.rubric_snapshot_json,
        explanation=application.explanation,
        status=application.status,
    )


@router.post("/applications", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    data: ApplicationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("startup")),
):
    startup = session.exec(select(Startup).where(Startup.user_id == current_user.id)).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup profile not found")

    if not session.get(Challenge, data.challenge_id):
        raise HTTPException(status_code=404, detail="Challenge not found")

    existing = session.exec(
        select(Application).where(
            Application.challenge_id == data.challenge_id,
            Application.startup_id == startup.id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Startup has already applied to this challenge")

    challenge = session.get(Challenge, data.challenge_id)
    rubric = resolve_rubric(session, challenge.match_rubric_id, "match")
    scored = score_application(challenge, startup, rubric.weights_json if rubric else {}, quote=data.quote)

    application = Application(
        challenge_id=data.challenge_id,
        startup_id=startup.id,
        quote=data.quote,
        pitch=data.pitch,
        eligible=scored["eligible"],
        eligibility_report_json=scored["eligibility_report"],
        match_score=scored["match_score"],
        match_breakdown_json=scored["match_breakdown"],
        rubric_snapshot_json=scored["rubric_snapshot"],
        explanation=scored["explanation"],
        status="applied",
        applied_at=datetime.now(timezone.utc),
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return _application_read(session, application)


@router.get("/applications", response_model=list[ApplicationRead])
def list_my_applications(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("startup")),
):
    startup = session.exec(select(Startup).where(Startup.user_id == current_user.id)).first()
    if not startup:
        return []

    applications = session.exec(
        select(Application).where(Application.startup_id == startup.id)
    ).all()
    return [_application_read(session, a) for a in applications]


@router.get("/applications/{application_id}", response_model=ApplicationRead)
def get_application(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "expert", "startup")),
):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "startup":
        startup = session.exec(select(Startup).where(Startup.user_id == current_user.id)).first()
        if not startup or startup.id != application.startup_id:
            raise HTTPException(status_code=403, detail="You do not have access to this application")

    return _application_read(session, application)


@router.post("/applications/{application_id}/shortlist", response_model=ApplicationShortlistOut)
def shortlist_application(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government")),
):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = "shortlisted"
    session.add(application)
    session.commit()
    return ApplicationShortlistOut(application_id=application.id, status=application.status)


@router.post("/applications/{application_id}/select", response_model=ApplicationSelectOut)
def select_application(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government")),
):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    challenge = session.get(Challenge, application.challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    others = session.exec(
        select(Application).where(
            Application.challenge_id == application.challenge_id,
            Application.id != application.id,
        )
    ).all()
    for other in others:
        other.status = "rejected"
        session.add(other)

    application.status = "selected"
    session.add(application)

    challenge.status = "selected"
    session.add(challenge)

    session.commit()
    return ApplicationSelectOut(
        application_id=application.id,
        status=application.status,
        challenge_status=challenge.status,
    )
