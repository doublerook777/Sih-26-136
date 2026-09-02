from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_user, require_role
from app.db import get_session
from app.models import Application, Challenge, Startup, User
from app.schemas import ApplicationCreate, ApplicationRead

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

    # Day 3 owns screening and matching. Keep their result columns at model defaults here.
    application = Application(
        challenge_id=data.challenge_id,
        startup_id=startup.id,
        status="applied",
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return _application_read(session, application)


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
