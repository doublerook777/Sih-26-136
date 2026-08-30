from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.db import create_db_and_tables, get_session
from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models import User,Challenge,Startup,Application
from app.engines.matching import match_startup

app = FastAPI()
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "SIH Backend is running"}
@app.post("/auth/register")
def register(
    user_data: User,
    session: Session = Depends(get_session),
):
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    user_data.password_hash = hash_password(user_data.password_hash)

    session.add(user_data)
    session.commit()
    session.refresh(user_data)

    return {
        "id": user_data.id,
        "name": user_data.name,
        "email": user_data.email,
        "role": user_data.role,
    }


@app.post("/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/auth/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
@app.get("/challenges")
def get_challenges(
    session: Session = Depends(get_session),
):
    return session.exec(select(Challenge)).all()


@app.get("/startups")
def get_startups(
    session: Session = Depends(get_session),
):
    return session.exec(select(Startup)).all()
@app.post("/challenges/{challenge_id}/discover")
def discover_startups(
    challenge_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "government":
        raise HTTPException(
            status_code=403,
            detail="Government role required",
        )

    challenge = session.get(Challenge, challenge_id)

    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found",
        )

    startups = session.exec(select(Startup)).all()

    results = []

    for startup in startups:
        result = match_startup(startup, challenge)

        application = Application(
            challenge_id=challenge.id,
            startup_id=startup.id,
            eligible=result["eligible"],
            eligibility_report_json=result["eligibility_report"],
            match_score=result["match_score"],
            match_breakdown_json=result["match_breakdown"],
            rubric_snapshot_json=result["rubric_snapshot"],
            explanation=result["explanation"],
            status="screened",
        )

        session.add(application)
        session.commit()
        session.refresh(application)

        results.append({
            "application_id": application.id,
            "startup_id": startup.id,
            "startup_name": startup.name,
            **result,
            "status": application.status,
        })

    results.sort(
        key=lambda x: (
            x["eligible"],
            x["match_score"]
        ),
        reverse=True,
    )

    return results
@app.get("/challenges/{challenge_id}/applications")
def get_challenge_applications(
    challenge_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["government", "expert"]:
        raise HTTPException(
            status_code=403,
            detail="Government or expert role required",
        )

    challenge = session.get(Challenge, challenge_id)

    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found",
        )

    applications = session.exec(
        select(Application).where(
            Application.challenge_id == challenge_id
        )
    ).all()

    results = []

    for application in applications:
        startup = session.get(Startup, application.startup_id)

        results.append({
            "application_id": application.id,
            "startup_id": application.startup_id,
            "startup_name": startup.name if startup else None,
            "eligible": application.eligible,
            "eligibility_report": application.eligibility_report_json,
            "match_score": application.match_score,
            "match_breakdown": application.match_breakdown_json,
            "rubric_snapshot": application.rubric_snapshot_json,
            "explanation": application.explanation,
            "status": application.status,
        })

    results.sort(
        key=lambda x: (
            x["eligible"],
            x["match_score"] or 0
        ),
        reverse=True,
    )

    return results
@app.get("/health")
def health():
    return {"status": "ok"}
