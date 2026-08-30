from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.auth import get_current_user
from app.db import get_session
from app.models import Application, Challenge, Startup, User
from app.schemas import ChallengeDetail, ChallengeListItem

router = APIRouter(tags=["challenges"])


def _application_count(session: Session, challenge_id: int) -> int:
    return session.exec(
        select(func.count()).select_from(Application).where(Application.challenge_id == challenge_id)
    ).one()


@router.get("/challenges", response_model=list[ChallengeListItem])
def list_challenges(
    sector: Optional[str] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(Challenge)
    if sector:
        query = query.where(Challenge.sector == sector)
    if status:
        query = query.where(Challenge.status == status)

    challenges = session.exec(query).all()
    return [
        ChallengeListItem(
            id=c.id,
            title=c.title,
            department=c.department,
            district=c.district,
            sector=c.sector,
            budget=c.budget,
            timeline_days=c.timeline_days,
            deadline=c.deadline,
            status=c.status,
            required_tech=c.required_tech,
            application_count=_application_count(session, c.id),
            created_at=None,  # add a real created_at column when there's time; not in models.py yet
            raw_description=c.raw_description,
        )
        for c in challenges
    ]


@router.get("/challenges/{challenge_id}", response_model=ChallengeDetail)
def get_challenge(
    challenge_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    return ChallengeDetail(
        id=challenge.id,
        title=challenge.title,
        department=challenge.department,
        district=challenge.district,
        sector=challenge.sector,
        budget=challenge.budget,
        timeline_days=challenge.timeline_days,
        deadline=challenge.deadline,
        status=challenge.status,
        required_tech=challenge.required_tech,
        application_count=_application_count(session, challenge.id),
        created_at=None,
        raw_description=challenge.raw_description,
        created_by=challenge.created_by,
        match_rubric_id=challenge.match_rubric_id,
        evaluation_rubric_id=challenge.evaluation_rubric_id,
        statement=challenge.statement_json,
        eligibility_rules=challenge.eligibility_rules_json,
        kpi_targets=challenge.kpi_targets_json,
    )


@router.get("/challenges/{challenge_id}/applications")
def get_challenge_applications(
    challenge_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("government", "expert"):
        raise HTTPException(status_code=403, detail="Government or expert role required")

    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    applications = session.exec(
        select(Application).where(Application.challenge_id == challenge_id)
    ).all()

    results = []
    for app_row in applications:
        startup = session.get(Startup, app_row.startup_id)
        results.append({
            "application_id": app_row.id,
            "startup_id": app_row.startup_id,
            "startup_name": startup.name if startup else None,
            "eligible": app_row.eligible,
            "eligibility_report": app_row.eligibility_report_json,
            "match_score": app_row.match_score,
            "match_breakdown": app_row.match_breakdown_json,
            "rubric_snapshot": app_row.rubric_snapshot_json,
            "explanation": app_row.explanation,
            "status": app_row.status,
        })

    results.sort(key=lambda x: (x["eligible"], x["match_score"] or 0), reverse=True)
    return results


# NOTE: POST /challenges/{id}/discover is intentionally NOT included today.
# It depends on Pair C's engines/matching.py, which is being written today
# (Day 2) and does not exist yet on `dev` in its real form. It is also a
# Day 3 task per the roadmap, not Day 1/2. Do not re-add a stub that calls a
# hand-rolled matching function — wait for C1's real score_match() and wire
# this properly once it lands, using a rubric's weights rather than a
# hardcoded dict.
