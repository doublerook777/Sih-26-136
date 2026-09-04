from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_user, require_role
from app.db import get_session
from app.models import Challenge, KPI, Milestone, Payment, Pilot, Procurement, Risk, Startup, User, Validation
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
    PilotFinalizeOut,
    PilotProcurementOut,
    PilotSummary,
    ProcurementChecks,
    ReplicateIn,
    ReplicateOut,
    ReplicationItem,
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
        claimed_value=m.claimed_value,
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


# ---------------------------------------------------------------------------
# 7. POST /pilots/{id}/finalize (Scale-up decision & final performance score)
# ---------------------------------------------------------------------------

@router.post("/pilots/{pilot_id}/finalize", response_model=PilotFinalizeOut)
def finalize_pilot(
    pilot_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "admin")),
):
    pilot = session.get(Pilot, pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    kpis = session.exec(select(KPI).where(KPI.pilot_id == pilot.id)).all()
    milestones = session.exec(select(Milestone).where(Milestone.pilot_id == pilot.id)).all()

    # Calculate security score from checklist
    checklist = pilot.security_checklist_json or {}
    if checklist:
        passed_sec = sum(1 for v in checklist.values() if v is True)
        total_sec = len(checklist)
        security_score = round((passed_sec / float(total_sec)) * 100.0, 1)
    else:
        security_score = 100.0 if pilot.security_status == "passed" else 0.0

    # Section 7b weights: 30/20/20/15/15
    weights = {
        "technical": 30,
        "cost": 20,
        "impact": 20,
        "scalability": 15,
        "security": 15,
    }

    # Group KPIs by category
    kpis_by_cat: dict[str, list[float]] = {"technical": [], "cost": [], "impact": [], "scalability": []}
    for k in kpis:
        cat = k.category.lower() if k.category else "technical"
        if cat in kpis_by_cat:
            ach_pct, _ = _compute_kpi_achievement(k.baseline, k.target, k.achieved, k.direction)
            val = ach_pct if ach_pct is not None else 100.0
            kpis_by_cat[cat].append(val)

    category_scores: dict[str, float] = {}
    for cat in ["technical", "cost", "impact", "scalability"]:
        scores = kpis_by_cat[cat]
        if scores:
            category_scores[cat] = round(sum(scores) / float(len(scores)), 1)
        else:
            category_scores[cat] = 100.0
    category_scores["security"] = security_score

    # Check if Pair C engines are available
    try:
        from app.engines.performance import final_score as engine_final_score
        from app.engines.decision import decide as engine_decide
        calc_result = engine_final_score(kpis=[k.model_dump() for k in kpis], security_score=security_score)
        final_score = calc_result["final_score"]
        category_scores = calc_result.get("category_scores", category_scores)
        decision = engine_decide(final_score=final_score)["decision"]
    except Exception:
        # Standard weighted calculation per Section 7b
        weighted_sum = (
            category_scores["technical"] * (weights["technical"] / 100.0)
            + category_scores["cost"] * (weights["cost"] / 100.0)
            + category_scores["impact"] * (weights["impact"] / 100.0)
            + category_scores["scalability"] * (weights["scalability"] / 100.0)
            + category_scores["security"] * (weights["security"] / 100.0)
        )
        final_score = round(weighted_sum, 1)

        # Decision thresholds (85/70/55)
        if final_score >= 85.0:
            decision = "scale"
        elif final_score >= 70.0:
            decision = "scale_with_modifications"
        elif final_score >= 55.0:
            decision = "extend_pilot"
        else:
            decision = "reject"

    # Justification with real numbers from this pilot
    total_m = len(milestones)
    val_m = sum(1 for m in milestones if m.status in ["validated", "paid"])
    impact_score = category_scores.get("impact", 0.0)
    tech_score = category_scores.get("technical", 0.0)
    cost_score = category_scores.get("cost", 0.0)
    sec_score = category_scores.get("security", 0.0)

    justification = (
        f"Pilot scored {final_score:.1f}/100 with {decision.replace('_', ' ')} recommendation. "
        f"Impact KPI score: {impact_score:.1f}%, Technical: {tech_score:.1f}%, Cost: {cost_score:.1f}%, "
        f"Cybersecurity audit: {sec_score:.1f}% ({pilot.security_status}), "
        f"{val_m} of {total_m} milestones validated."
    )

    # Save or update Procurement table row
    procurement = session.exec(select(Procurement).where(Procurement.pilot_id == pilot.id)).first()
    pathway = "GeM direct procurement" if final_score >= 85.0 else "Custom / Cautious procurement"
    if not procurement:
        procurement = Procurement(
            pilot_id=pilot.id,
            final_score=final_score,
            decision=decision,
            pathway=pathway,
            justification=justification,
            replication_json=[{"district": pilot.location, "status": "completed"}],
        )
        session.add(procurement)
    else:
        procurement.final_score = final_score
        procurement.decision = decision
        procurement.pathway = pathway
        procurement.justification = justification
        session.add(procurement)

    # Update pilot status
    if decision == "scale":
        pilot.status = "completed"
        session.add(pilot)

    session.commit()

    return PilotFinalizeOut(
        pilot_id=pilot.id,
        category_scores=category_scores,
        weights=weights,
        final_score=final_score,
        decision=decision,
        justification=justification,
    )


# ---------------------------------------------------------------------------
# 8. GET /pilots/{id}/procurement (Read-only procurement readiness checks)
# ---------------------------------------------------------------------------

@router.get("/pilots/{pilot_id}/procurement", response_model=PilotProcurementOut)
def get_pilot_procurement(
    pilot_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "validator", "startup", "admin")),
):
    pilot = session.get(Pilot, pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    milestones = session.exec(select(Milestone).where(Milestone.pilot_id == pilot.id)).all()
    procurement = session.exec(select(Procurement).where(Procurement.pilot_id == pilot.id)).first()

    # Four real boolean checks (never hardcoded):
    # 1. pilot_validated: all milestones validated or paid
    pilot_validated = len(milestones) > 0 and all(m.status in ["validated", "paid"] for m in milestones)

    # 2. performance_threshold_met: final_score >= 85.0
    final_score = procurement.final_score if procurement else None
    performance_threshold_met = bool(final_score is not None and final_score >= 85.0)

    # 3. security_approved: security_status == 'passed'
    security_approved = bool(pilot.security_status == "passed")

    # 4. budget_available: positive budget allocated and not exceeded
    paid_to_date = sum(m.amount for m in milestones if m.status == "paid")
    budget_available = bool(pilot.budget > 0 and paid_to_date <= pilot.budget)

    # Determine recommended pathway
    if performance_threshold_met and security_approved and pilot_validated:
        recommended_pathway = "GeM direct procurement"
    elif performance_threshold_met or (final_score is not None and final_score >= 70.0):
        recommended_pathway = "Special procurement with phased rollout"
    else:
        recommended_pathway = "Conditional extension / Re-evaluation"

    # Replication list
    if procurement and isinstance(procurement.replication_json, list) and procurement.replication_json:
        replication = [
            ReplicationItem(district=r["district"], status=r["status"])
            for r in procurement.replication_json
            if isinstance(r, dict) and "district" in r and "status" in r
        ]
    else:
        replication = [ReplicationItem(district=pilot.location, status="completed")]

    return PilotProcurementOut(
        pilot_id=pilot.id,
        final_score=final_score,
        decision=procurement.decision if procurement else None,
        checks=ProcurementChecks(
            pilot_validated=pilot_validated,
            performance_threshold_met=performance_threshold_met,
            security_approved=security_approved,
            budget_available=budget_available,
        ),
        recommended_pathway=procurement.pathway if (procurement and procurement.pathway) else recommended_pathway,
        justification=procurement.justification if (procurement and procurement.justification) else None,
        replication=replication,
    )


# ---------------------------------------------------------------------------
# 9. POST /pilots/{id}/replicate (Append districts for scale-up replication)
# ---------------------------------------------------------------------------

@router.post("/pilots/{pilot_id}/replicate", response_model=ReplicateOut)
def replicate_pilot(
    pilot_id: int,
    data: ReplicateIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "admin")),
):
    pilot = session.get(Pilot, pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    procurement = session.exec(select(Procurement).where(Procurement.pilot_id == pilot.id)).first()
    if not procurement:
        procurement = Procurement(
            pilot_id=pilot.id,
            decision="scale",
            pathway="GeM direct procurement",
            replication_json=[{"district": pilot.location, "status": "completed"}],
        )
        session.add(procurement)

    # Appends districts to replication_json list, each starting at 'planned', existing entries keep status.
    # Calling replicate a second time with an already-listed district doesn't duplicate it.
    existing_reps = list(procurement.replication_json) if isinstance(procurement.replication_json, list) else []
    existing_districts = {
        r["district"]: r for r in existing_reps if isinstance(r, dict) and "district" in r
    }

    if pilot.location not in existing_districts:
        base_item = {"district": pilot.location, "status": "completed"}
        existing_reps.insert(0, base_item)
        existing_districts[pilot.location] = base_item

    for district_name in data.districts:
        clean_name = district_name.strip()
        if clean_name and clean_name not in existing_districts:
            new_item = {"district": clean_name, "status": "planned"}
            existing_reps.append(new_item)
            existing_districts[clean_name] = new_item

    procurement.replication_json = existing_reps
    session.add(procurement)
    session.commit()
    session.refresh(procurement)

    return ReplicateOut(
        pilot_id=pilot.id,
        replication=[
            ReplicationItem(district=r["district"], status=r["status"])
            for r in procurement.replication_json
            if isinstance(r, dict) and "district" in r and "status" in r
        ],
    )

