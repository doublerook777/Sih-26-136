from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select, func

from app.db import create_db_and_tables, get_session
from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
    require_role,
)
from app.models import (
    User,
    Challenge,
    Startup,
    Application,
    Evaluation,
    Rubric,
    Pilot,
    Milestone,
    KPI,
    Risk,
    Procurement,
)
from app.engines.matching import match_startup
from app.ai.problem_statement import generate_problem_statement
from app.routers import documents

app = FastAPI(title="ProcuraAI Backend", version="1.0.0")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Documents router (Jinja2 templates rendering)
app.include_router(documents.router)


# -----------------------------------------------------------------------------
# Pydantic Schemas for Requests
# -----------------------------------------------------------------------------
class ChallengeCreateRequest(BaseModel):
    title: str
    raw_description: str
    department: str
    district: str
    sector: str
    budget: Optional[int] = None
    timeline_days: Optional[int] = None
    deadline: Optional[Any] = None
    required_tech: Optional[List[str]] = []
    match_rubric_id: Optional[int] = None
    evaluation_rubric_id: Optional[int] = None
    statement: Optional[Dict[str, Any]] = None
    statement_json: Optional[Dict[str, Any]] = None
    eligibility_rules: Optional[Dict[str, Any]] = None
    eligibility_rules_json: Optional[Dict[str, Any]] = None
    kpi_targets: Optional[List[Dict[str, Any]]] = None
    kpi_targets_json: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = "draft"


class ApplicationCreateRequest(BaseModel):
    challenge_id: int
    quote: Optional[int] = None
    pitch: Optional[str] = None
    startup_id: Optional[int] = None


class GenerateStatementRequest(BaseModel):
    raw_description: str
    title: Optional[str] = ""
    department: Optional[str] = ""
    district: Optional[str] = ""
    sector: Optional[str] = ""
    budget: Optional[int] = None
    timeline_days: Optional[int] = None


# -----------------------------------------------------------------------------
# System & Auth Endpoints
# -----------------------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "ProcuraAI Backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


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
            status_code=status.HTTP_400_BAD_REQUEST,
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
        "department": user_data.department,
        "district": user_data.district,
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
            status_code=status.HTTP_401_UNAUTHORIZED,
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
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "department": current_user.department,
        "district": current_user.district,
    }


# -----------------------------------------------------------------------------
# AI Problem Statement Generation
# -----------------------------------------------------------------------------
@app.post("/ai/generate-statement")
def ai_generate_statement(
    req: GenerateStatementRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generates the strict 15-section problem statement JSON.
    Falls back gracefully to template if LLM is offline.
    """
    if current_user.role not in ["government", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Government role required",
        )

    result = generate_problem_statement(req.model_dump())
    return result


# -----------------------------------------------------------------------------
# Challenges Endpoints (Day 2 Deliverable)
# -----------------------------------------------------------------------------
@app.get("/challenges")
def get_challenges(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    status: Optional[str] = Query(None, description="Filter by status"),
    session: Session = Depends(get_session),
):
    query = select(Challenge)
    if sector:
        query = query.where(Challenge.sector == sector.lower())
    if status:
        query = query.where(Challenge.status == status.lower())

    challenges = session.exec(query).all()

    # Build response with application counts
    results = []
    for c in challenges:
        app_count = session.exec(
            select(func.count(Application.id)).where(Application.challenge_id == c.id)
        ).one()

        deadline_str = c.deadline.isoformat() if isinstance(c.deadline, (date, datetime)) else c.deadline

        results.append({
            "id": c.id,
            "created_by": c.created_by,
            "title": c.title,
            "raw_description": c.raw_description,
            "department": c.department,
            "district": c.district,
            "sector": c.sector,
            "budget": c.budget,
            "timeline_days": c.timeline_days,
            "deadline": deadline_str,
            "status": c.status,
            "required_tech": c.required_tech or [],
            "application_count": app_count,
            "match_rubric_id": c.match_rubric_id,
            "evaluation_rubric_id": c.evaluation_rubric_id,
        })

    return results


@app.post("/challenges", status_code=status.HTTP_201_CREATED)
def create_challenge(
    data: ChallengeCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Creates and persists a new challenge along with its 15-section problem statement.
    Role: government (or admin).
    """
    if current_user.role not in ["government", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Government role required",
        )

    # Resolve 15-section problem statement
    statement = data.statement or data.statement_json
    if not statement:
        statement = generate_problem_statement({
            "title": data.title,
            "raw_description": data.raw_description,
            "department": data.department,
            "district": data.district,
            "sector": data.sector,
            "budget": data.budget,
            "timeline_days": data.timeline_days,
        })

    # Resolve rules and KPIs
    eligibility_rules = data.eligibility_rules or data.eligibility_rules_json or {}
    kpi_targets = data.kpi_targets or data.kpi_targets_json or []

    # Parse deadline if provided as string
    parsed_deadline = None
    if data.deadline:
        if isinstance(data.deadline, (date, datetime)):
            parsed_deadline = data.deadline
        elif isinstance(data.deadline, str):
            try:
                parsed_deadline = datetime.strptime(data.deadline, "%Y-%m-%d").date()
            except ValueError:
                parsed_deadline = None

    challenge = Challenge(
        created_by=current_user.id,
        department=data.department,
        district=data.district,
        title=data.title,
        raw_description=data.raw_description,
        statement_json=statement,
        sector=data.sector.lower(),
        required_tech=data.required_tech or [],
        eligibility_rules_json=eligibility_rules,
        kpi_targets_json=kpi_targets,
        budget=data.budget,
        timeline_days=data.timeline_days,
        deadline=parsed_deadline,
        status=data.status or "draft",
        match_rubric_id=data.match_rubric_id,
        evaluation_rubric_id=data.evaluation_rubric_id,
    )

    session.add(challenge)
    session.commit()
    session.refresh(challenge)

    deadline_str = challenge.deadline.isoformat() if isinstance(challenge.deadline, (date, datetime)) else challenge.deadline

    return {
        "id": challenge.id,
        "created_by": challenge.created_by,
        "title": challenge.title,
        "raw_description": challenge.raw_description,
        "department": challenge.department,
        "district": challenge.district,
        "sector": challenge.sector,
        "budget": challenge.budget,
        "timeline_days": challenge.timeline_days,
        "deadline": deadline_str,
        "status": challenge.status,
        "required_tech": challenge.required_tech or [],
        "statement": challenge.statement_json or {},
        "statement_json": challenge.statement_json or {},
        "eligibility_rules": challenge.eligibility_rules_json or {},
        "eligibility_rules_json": challenge.eligibility_rules_json or {},
        "kpi_targets": challenge.kpi_targets_json or [],
        "kpi_targets_json": challenge.kpi_targets_json or [],
        "match_rubric_id": challenge.match_rubric_id,
        "evaluation_rubric_id": challenge.evaluation_rubric_id,
        "application_count": 0,
    }


@app.get("/challenges/{challenge_id}")
def get_challenge(
    challenge_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Returns full challenge object including statement, eligibility rules, and KPI targets.
    """
    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    app_count = session.exec(
        select(func.count(Application.id)).where(Application.challenge_id == challenge.id)
    ).one()

    deadline_str = challenge.deadline.isoformat() if isinstance(challenge.deadline, (date, datetime)) else challenge.deadline

    return {
        "id": challenge.id,
        "created_by": challenge.created_by,
        "title": challenge.title,
        "raw_description": challenge.raw_description,
        "department": challenge.department,
        "district": challenge.district,
        "sector": challenge.sector,
        "budget": challenge.budget,
        "timeline_days": challenge.timeline_days,
        "deadline": deadline_str,
        "status": challenge.status,
        "required_tech": challenge.required_tech or [],
        "statement": challenge.statement_json or {},
        "statement_json": challenge.statement_json or {},
        "eligibility_rules": challenge.eligibility_rules_json or {},
        "eligibility_rules_json": challenge.eligibility_rules_json or {},
        "kpi_targets": challenge.kpi_targets_json or [],
        "kpi_targets_json": challenge.kpi_targets_json or [],
        "match_rubric_id": challenge.match_rubric_id,
        "evaluation_rubric_id": challenge.evaluation_rubric_id,
        "application_count": app_count,
    }


# -----------------------------------------------------------------------------
# Startups Endpoints
# -----------------------------------------------------------------------------
@app.get("/startups")
def get_startups(
    sector: Optional[str] = Query(None),
    tech: Optional[str] = Query(None),
    session: Session = Depends(get_session),
):
    query = select(Startup)
    if sector:
        query = query.where(Startup.sector == sector.lower())
    startups = session.exec(query).all()

    if tech:
        tech_lower = tech.lower()
        startups = [
            s for s in startups
            if any(tech_lower in t.lower() for t in (s.technologies or []))
        ]

    return startups


@app.get("/startups/{startup_id}")
def get_startup(
    startup_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    startup = session.get(Startup, startup_id)
    if not startup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found",
        )
    return startup


# -----------------------------------------------------------------------------
# Applications & Discovery Endpoints (Day 2 Deliverables)
# -----------------------------------------------------------------------------
@app.post("/applications", status_code=status.HTTP_201_CREATED)
def apply_to_challenge(
    data: ApplicationCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    A startup applies to a challenge.
    Runs eligibility and match scoring, persists application with status 'applied'.
    Role: startup (or admin).
    """
    if current_user.role not in ["startup", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Startup role required",
        )

    # Find the startup profile for current user (or specified startup_id if admin)
    startup = None
    if data.startup_id and current_user.role == "admin":
        startup = session.get(Startup, data.startup_id)
    else:
        startup = session.exec(
            select(Startup).where(Startup.user_id == current_user.id)
        ).first()

    if not startup:
        # Fallback: check if startup ID matches current_user.id in seeded single-user data
        startup = session.get(Startup, current_user.id)

    if not startup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found for this user",
        )

    challenge = session.get(Challenge, data.challenge_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    # Run eligibility and matching engine
    result = match_startup(startup, challenge)

    # Check if application already exists
    existing_app = session.exec(
        select(Application).where(
            Application.challenge_id == challenge.id,
            Application.startup_id == startup.id,
        )
    ).first()

    if existing_app:
        application = existing_app
        application.eligible = result["eligible"]
        application.eligibility_report_json = result["eligibility_report"]
        application.match_score = result["match_score"]
        application.match_breakdown_json = result["match_breakdown"]
        application.rubric_snapshot_json = result["rubric_snapshot"]
        application.explanation = result["explanation"]
        application.status = "applied"
    else:
        application = Application(
            challenge_id=challenge.id,
            startup_id=startup.id,
            eligible=result["eligible"],
            eligibility_report_json=result["eligibility_report"],
            match_score=result["match_score"],
            match_breakdown_json=result["match_breakdown"],
            rubric_snapshot_json=result["rubric_snapshot"],
            explanation=result["explanation"],
            status="applied",
        )
        session.add(application)

    session.commit()
    session.refresh(application)

    return {
        "application_id": application.id,
        "startup_id": startup.id,
        "startup_name": startup.name,
        "eligible": application.eligible,
        "eligibility_report": application.eligibility_report_json,
        "match_score": application.match_score,
        "match_breakdown": application.match_breakdown_json,
        "rubric_snapshot": application.rubric_snapshot_json,
        "explanation": application.explanation,
        "status": application.status,
    }


@app.get("/challenges/{challenge_id}/applications")
def get_challenge_applications(
    challenge_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Returns screened applications for a challenge.
    Roles: government, expert, admin.
    """
    if current_user.role not in ["government", "expert", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Government or expert role required",
        )

    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    applications = session.exec(
        select(Application).where(Application.challenge_id == challenge_id)
    ).all()

    results = []
    for application in applications:
        startup = session.get(Startup, application.startup_id)
        results.append({
            "application_id": application.id,
            "startup_id": application.startup_id,
            "startup_name": startup.name if startup else f"Startup #{application.startup_id}",
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
            1 if x["eligible"] else 0,
            x["match_score"] or 0
        ),
        reverse=True,
    )

    return results


@app.post("/challenges/{challenge_id}/discover")
def discover_startups(
    challenge_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["government", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Government role required",
        )

    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    startups = session.exec(select(Startup)).all()
    results = []

    for startup in startups:
        result = match_startup(startup, challenge)

        existing_app = session.exec(
            select(Application).where(
                Application.challenge_id == challenge.id,
                Application.startup_id == startup.id,
            )
        ).first()

        if existing_app:
            application = existing_app
            application.eligible = result["eligible"]
            application.eligibility_report_json = result["eligibility_report"]
            application.match_score = result["match_score"]
            application.match_breakdown_json = result["match_breakdown"]
            application.rubric_snapshot_json = result["rubric_snapshot"]
            application.explanation = result["explanation"]
            application.status = "screened"
        else:
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
            1 if x["eligible"] else 0,
            x["match_score"] or 0
        ),
        reverse=True,
    )

    return results
