from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_user, require_role
from app.db import get_session
from app.models import Challenge, KPI, Milestone, Payment, Pilot, Risk, Startup, User, Validation
from app.schemas import (
    KPICreate,
    KPIRead,
    KPIUpdate,
    MilestoneCreate,
    MilestonePaymentRead,
    MilestoneRead,
    MilestoneValidationRead,
    PilotCreate,
    PilotCreateResponse,
    PilotDetail,
    PilotSummary,
    RiskCreate,
    RiskRead,
    SecurityCheckIn,
    SecurityCheckOut,
)

router = APIRouter(tags=["pilots"])


def _compute_kpi_achievement(
    baseline: Optional[float],
    target: Optional[float],
    achieved: Optional[float],
    direction: str,
) -> tuple[Optional[float], bool]:
    """
    Computes achievement percentage for a KPI, respecting direction and capped at 120.0 (1.2x).
    Returns (achievement_percentage, met_boolean).
    """
    if achieved is None:
        return None, False
    if baseline is None or target is None:
        return 0.0, False

    span = abs(target - baseline)
    if span == 0:
        ratio = 1.0 if achieved >= target else 0.0
    else:
        gain = abs(achieved - baseline)
        wrong_way = (
            (direction == "lower_is_better" and achieved > baseline)
            or (direction == "higher_is_better" and achieved < baseline)
        )
        if wrong_way:
            gain = -gain
        ratio = max(0.0, min(gain / span, 1.2))

    achievement_pct = round(ratio * 100.0, 1)
    met = achievement_pct >= 100.0
    return achievement_pct, met


def _calculate_risk_level(risks: List[Risk]) -> Optional[str]:
    """
    Risk level thresholds:
    - max_score >= 15 -> 'high'
    - max_score >= 8  -> 'medium'
    - otherwise       -> 'low'
    If no risks exist, returns None.
    """
    if not risks:
        return None
    max_score = max(r.score for r in risks)
    if max_score >= 15:
        return "high"
    elif max_score >= 8:
        return "medium"
    else:
        return "low"


def _build_milestone_read(session: Session, m: Milestone) -> MilestoneRead:
    validation = session.exec(select(Validation).where(Validation.milestone_id == m.id)).first()
    payment = session.exec(select(Payment).where(Payment.milestone_id == m.id)).first()

    val_read: Optional[MilestoneValidationRead] = None
    if validation:
        validator_user = session.get(User, validation.validator_id) if validation.validator_id else None
        val_read = MilestoneValidationRead(
            verdict=validation.verdict,
            claimed_value=validation.claimed_value,
            verified_value=validation.verified_value,
            validator_name=validator_user.name if validator_user else None,
            notes=validation.evidence_notes,
            validated_at=validation.validated_at,
        )

    pay_read: Optional[MilestonePaymentRead] = None
    if payment:
        pay_read = MilestonePaymentRead(
            status=payment.status,
            amount=payment.amount,
            mock_txn_ref=payment.mock_txn_ref,
            released_at=payment.released_at,
        )

    return MilestoneRead(
        id=m.id,
        seq=m.seq,
        title=m.title,
        deliverable=m.deliverable,
        amount=m.amount,
        due_date=m.due_date,
        status=m.status,
        evidence_text=m.evidence_text,
        evidence_url=m.evidence_url,
        submitted_at=m.submitted_at,
        validation=val_read,
        payment=pay_read,
    )


def _build_kpi_read(k: KPI) -> KPIRead:
    achievement_val, met_val = _compute_kpi_achievement(
        baseline=k.baseline,
        target=k.target,
        achieved=k.achieved,
        direction=k.direction,
    )
    return KPIRead(
        id=k.id,
        name=k.name,
        unit=k.unit,
        baseline=k.baseline,
        target=k.target,
        achieved=k.achieved,
        category=k.category,
        direction=k.direction,
        achievement=achievement_val,
        met=met_val,
    )


# ---------------------------------------------------------------------------
# 1. POST /pilots (Create pilot with milestones and KPIs)
# ---------------------------------------------------------------------------

@router.post("/pilots", response_model=PilotCreateResponse, status_code=status.HTTP_201_CREATED)
def create_pilot(
    data: PilotCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "admin")),
):
    # Validate before touching database: milestone amounts must sum to pilot budget
    if sum(m.amount for m in data.milestones) != data.budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Milestone amounts must sum to the pilot budget",
        )

    challenge = session.get(Challenge, data.challenge_id)
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")

    startup = session.get(Startup, data.startup_id)
    if not startup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    # Create Pilot row
    pilot = Pilot(
        challenge_id=data.challenge_id,
        startup_id=data.startup_id,
        location=data.location,
        duration_days=data.duration_days,
        budget=data.budget,
        objectives=data.objectives,
        security_checklist_json={},
        security_status="pending",
        risk_level=None,
        status="created",
    )
    session.add(pilot)
    session.flush()

    # Create Milestones
    milestone_objects: List[MilestoneRead] = []
    for m in data.milestones:
        milestone = Milestone(
            pilot_id=pilot.id,
            seq=m.seq,
            title=m.title,
            deliverable=m.deliverable,
            amount=m.amount,
            due_date=m.due_date,
            status="pending",
            evidence_text=None,
            evidence_url=None,
            submitted_at=None,
        )
        session.add(milestone)
        session.flush()
        milestone_objects.append(_build_milestone_read(session, milestone))

    # Create KPIs
    kpi_objects: List[KPIRead] = []
    for k in data.kpis:
        kpi = KPI(
            pilot_id=pilot.id,
            name=k.name,
            unit=k.unit,
            baseline=k.baseline,
            target=k.target,
            achieved=None,
            met=False,
            category=k.category,
            direction=k.direction,
        )
        session.add(kpi)
        session.flush()
        kpi_objects.append(_build_kpi_read(kpi))

    session.commit()
    session.refresh(pilot)

    return PilotCreateResponse(
        id=pilot.id,
        challenge_id=pilot.challenge_id,
        startup_id=pilot.startup_id,
        startup_name=startup.name,
        location=pilot.location,
        duration_days=pilot.duration_days,
        budget=pilot.budget,
        objectives=pilot.objectives,
        status=pilot.status,
        security_status=pilot.security_status,
        risk_level=pilot.risk_level,
        milestones=milestone_objects,
        kpis=kpi_objects,
        created_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# 2. GET /pilots (List pilots summary)
# ---------------------------------------------------------------------------

@router.get("/pilots", response_model=List[PilotSummary])
def list_pilots(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "validator", "startup", "admin")),
):
    query = select(Pilot)
    if current_user.role == "startup":
        startup = session.exec(select(Startup).where(Startup.user_id == current_user.id)).first()
        if not startup:
            return []
        query = query.where(Pilot.startup_id == startup.id)

    pilots = session.exec(query).all()
    summaries: List[PilotSummary] = []

    for pilot in pilots:
        challenge = session.get(Challenge, pilot.challenge_id)
        startup = session.get(Startup, pilot.startup_id)
        milestones = session.exec(select(Milestone).where(Milestone.pilot_id == pilot.id)).all()

        milestones_total = len(milestones)
        milestones_paid = sum(1 for m in milestones if m.status == "paid")
        paid_to_date = sum(m.amount for m in milestones if m.status == "paid")

        summaries.append(
            PilotSummary(
                id=pilot.id,
                challenge_title=challenge.title if challenge else "Unknown",
                startup_name=startup.name if startup else "Unknown",
                location=pilot.location,
                status=pilot.status,
                budget=pilot.budget,
                paid_to_date=paid_to_date,
                milestones_total=milestones_total,
                milestones_paid=milestones_paid,
                security_status=pilot.security_status,
                risk_level=pilot.risk_level,
            )
        )

    return summaries


# ---------------------------------------------------------------------------
# 3. GET /pilots/{id} (Deep nested pilot details)
# ---------------------------------------------------------------------------

@router.get("/pilots/{pilot_id}", response_model=PilotDetail)
def get_pilot_detail(
    pilot_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "validator", "startup", "admin")),
):
    pilot = session.get(Pilot, pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    if current_user.role == "startup":
        startup = session.exec(select(Startup).where(Startup.user_id == current_user.id)).first()
        if not startup or startup.id != pilot.startup_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this pilot",
            )

    challenge = session.get(Challenge, pilot.challenge_id)
    startup = session.get(Startup, pilot.startup_id)

    milestones = session.exec(
        select(Milestone).where(Milestone.pilot_id == pilot.id).order_by(Milestone.seq)
    ).all()
    milestone_objects = [_build_milestone_read(session, m) for m in milestones]
    paid_to_date = sum(m.amount for m in milestones if m.status == "paid")

    kpis = session.exec(select(KPI).where(KPI.pilot_id == pilot.id)).all()
    kpi_objects = [_build_kpi_read(k) for k in kpis]

    risks = session.exec(select(Risk).where(Risk.pilot_id == pilot.id)).all()
    risk_objects = [
        RiskRead(
            id=r.id,
            description=r.description,
            probability=r.probability,
            impact=r.impact,
            score=r.score,
            mitigation=r.mitigation,
            owner=r.owner,
        )
        for r in risks
    ]

    return PilotDetail(
        id=pilot.id,
        challenge_id=pilot.challenge_id,
        challenge_title=challenge.title if challenge else "Unknown",
        startup_id=pilot.startup_id,
        startup_name=startup.name if startup else "Unknown",
        location=pilot.location,
        duration_days=pilot.duration_days,
        budget=pilot.budget,
        paid_to_date=paid_to_date,
        status=pilot.status,
        security_status=pilot.security_status,
        risk_level=pilot.risk_level,
        milestones=milestone_objects,
        kpis=kpi_objects,
        risks=risk_objects,
        security_checklist=pilot.security_checklist_json or {},
    )


# ---------------------------------------------------------------------------
# 4. POST /pilots/{id}/security-check (8-item checklist check)
# ---------------------------------------------------------------------------

@router.post("/pilots/{pilot_id}/security-check", response_model=SecurityCheckOut)
def run_security_check(
    pilot_id: int,
    data: SecurityCheckIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "admin")),
):
    pilot = session.get(Pilot, pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    checklist_dict = data.model_dump()
    passed_count = sum(1 for v in checklist_dict.values() if v is True)
    total_count = len(checklist_dict)  # exactly 8
    score = round((passed_count / float(total_count)) * 100.0, 1)
    failed = [k for k, v in checklist_dict.items() if not v]
    security_status = "passed" if passed_count == total_count else "needs_remediation"

    # Persist results to pilot
    pilot.security_status = security_status
    pilot.security_checklist_json = checklist_dict
    session.add(pilot)
    session.commit()
    session.refresh(pilot)

    return SecurityCheckOut(
        pilot_id=pilot.id,
        security_status=security_status,
        score=score,
        passed_count=passed_count,
        total_count=total_count,
        failed=failed,
    )


# ---------------------------------------------------------------------------
# 5. GET & POST /pilots/{id}/risks
# ---------------------------------------------------------------------------

@router.get("/pilots/{pilot_id}/risks", response_model=List[RiskRead])
def get_pilot_risks(
    pilot_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "validator", "startup", "admin")),
):
    pilot = session.get(Pilot, pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    if current_user.role == "startup":
        startup = session.exec(select(Startup).where(Startup.user_id == current_user.id)).first()
        if not startup or startup.id != pilot.startup_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this pilot",
            )

    risks = session.exec(select(Risk).where(Risk.pilot_id == pilot.id)).all()
    return [
        RiskRead(
            id=r.id,
            description=r.description,
            probability=r.probability,
            impact=r.impact,
            score=r.score,
            mitigation=r.mitigation,
            owner=r.owner,
        )
        for r in risks
    ]


@router.post("/pilots/{pilot_id}/risks", response_model=RiskRead, status_code=status.HTTP_201_CREATED)
def create_pilot_risk(
    pilot_id: int,
    data: RiskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "admin")),
):
    pilot = session.get(Pilot, pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    if not (1 <= data.probability <= 5 and 1 <= data.impact <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Probability and impact must be between 1 and 5",
        )

    # Server-side score computation: score = probability * impact
    score = data.probability * data.impact

    risk = Risk(
        pilot_id=pilot.id,
        description=data.description,
        probability=data.probability,
        impact=data.impact,
        score=score,
        mitigation=data.mitigation,
        owner=data.owner,
    )
    session.add(risk)
    session.flush()

    # Recompute and update pilot's overall risk level
    all_risks = session.exec(select(Risk).where(Risk.pilot_id == pilot.id)).all()
    pilot.risk_level = _calculate_risk_level(all_risks)
    session.add(pilot)

    session.commit()
    session.refresh(risk)

    return RiskRead(
        id=risk.id,
        description=risk.description,
        probability=risk.probability,
        impact=risk.impact,
        score=risk.score,
        mitigation=risk.mitigation,
        owner=risk.owner,
    )


# ---------------------------------------------------------------------------
# 6. GET & POST /pilots/{id}/kpis
# ---------------------------------------------------------------------------

@router.get("/pilots/{pilot_id}/kpis", response_model=List[KPIRead])
def get_pilot_kpis(
    pilot_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "validator", "startup", "admin")),
):
    pilot = session.get(Pilot, pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    if current_user.role == "startup":
        startup = session.exec(select(Startup).where(Startup.user_id == current_user.id)).first()
        if not startup or startup.id != pilot.startup_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this pilot",
            )

    kpis = session.exec(select(KPI).where(KPI.pilot_id == pilot.id)).all()
    return [_build_kpi_read(k) for k in kpis]


@router.post("/pilots/{pilot_id}/kpis", response_model=KPIRead)
def update_pilot_kpi(
    pilot_id: int,
    data: KPIUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "admin")),
):
    pilot = session.get(Pilot, pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    kpi = session.get(KPI, data.kpi_id)
    if not kpi or kpi.pilot_id != pilot.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found for this pilot")

    kpi.achieved = data.achieved
    achievement_val, met_val = _compute_kpi_achievement(
        baseline=kpi.baseline,
        target=kpi.target,
        achieved=kpi.achieved,
        direction=kpi.direction,
    )
    kpi.met = met_val

    session.add(kpi)
    session.commit()
    session.refresh(kpi)

    return KPIRead(
        id=kpi.id,
        name=kpi.name,
        unit=kpi.unit,
        baseline=kpi.baseline,
        target=kpi.target,
        achieved=kpi.achieved,
        category=kpi.category,
        direction=kpi.direction,
        achievement=achievement_val,
        met=kpi.met,
    )
