from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_user, require_role
from app.db import get_session
from app.models import Milestone, Payment, Pilot, Startup, User, Validation
from app.schemas import (
    MilestonePayOut,
    MilestonePaymentRead,
    MilestoneSubmitIn,
    MilestoneSubmitOut,
    MilestoneValidateIn,
    MilestoneValidateOut,
    MilestoneValidationRead,
)

router = APIRouter(tags=["milestones"])


# ---------------------------------------------------------------------------
# 1. POST /milestones/{id}/submit (Startup submits evidence)
# ---------------------------------------------------------------------------

@router.post("/milestones/{milestone_id}/submit", response_model=MilestoneSubmitOut)
def submit_milestone(
    milestone_id: int,
    data: MilestoneSubmitIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("startup", "admin")),
):
    milestone = session.get(Milestone, milestone_id)
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    pilot = session.get(Pilot, milestone.pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    # Role check: only the owning startup can submit
    if current_user.role == "startup":
        startup = session.exec(select(Startup).where(Startup.user_id == current_user.id)).first()
        if not startup or startup.id != pilot.startup_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owning startup can submit evidence for this milestone",
            )

    milestone.evidence_text = data.evidence_text
    milestone.evidence_url = data.evidence_url
    milestone.claimed_value = data.claimed_value
    milestone.submitted_at = datetime.now(timezone.utc)
    milestone.status = "submitted"

    session.add(milestone)
    session.commit()
    session.refresh(milestone)

    return MilestoneSubmitOut(
        id=milestone.id,
        status=milestone.status,
        submitted_at=milestone.submitted_at,
    )


# ---------------------------------------------------------------------------
# 2. POST /milestones/{id}/validate (Independent Validator validation)
# ---------------------------------------------------------------------------

@router.post("/milestones/{milestone_id}/validate", response_model=MilestoneValidateOut)
def validate_milestone(
    milestone_id: int,
    data: MilestoneValidateIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    milestone = session.get(Milestone, milestone_id)
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    pilot = session.get(Pilot, milestone.pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    # CRITICAL SECURITY RULE: The startup's own account attempting to validate its own milestone gets 403
    startup = session.get(Startup, pilot.startup_id)
    if current_user.role == "startup" or (startup and startup.user_id == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Startup cannot validate its own milestone",
        )

    # Must have validator or admin role
    if current_user.role not in ["validator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only validators can validate milestones",
        )

    verdict_clean = data.verdict.strip().lower()
    if verdict_clean not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verdict must be 'approved' or 'rejected'",
        )

    if verdict_clean == "approved":
        milestone.status = "validated"
    else:
        milestone.status = "rejected"

    validation = Validation(
        milestone_id=milestone.id,
        validator_id=current_user.id,
        claimed_value=milestone.claimed_value,
        verified_value=data.verified_value,
        verdict=verdict_clean,
        evidence_notes=data.notes,
        validated_at=datetime.now(timezone.utc),
    )
    session.add(validation)
    session.add(milestone)
    session.commit()
    session.refresh(milestone)
    session.refresh(validation)

    return MilestoneValidateOut(
        milestone_id=milestone.id,
        status=milestone.status,
        validation=MilestoneValidationRead(
            verdict=validation.verdict,
            claimed_value=validation.claimed_value,
            verified_value=validation.verified_value,
            validator_name=current_user.name,
            notes=validation.evidence_notes,
            validated_at=validation.validated_at,
        ),
    )


# ---------------------------------------------------------------------------
# 3. POST /milestones/{id}/pay (Government release mock payment)
# ---------------------------------------------------------------------------

@router.post("/milestones/{milestone_id}/pay", response_model=MilestonePayOut)
def pay_milestone(
    milestone_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "admin")),
):
    milestone = session.get(Milestone, milestone_id)
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    pilot = session.get(Pilot, milestone.pilot_id)
    if not pilot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pilot not found")

    # Idempotency rule: Paying an already-paid milestone doesn't double-pay,
    # returns existing payment record with 200 OK without creating duplicate payments.
    if milestone.status == "paid":
        existing_payment = session.exec(
            select(Payment).where(Payment.milestone_id == milestone.id)
        ).first()
        if existing_payment:
            return MilestonePayOut(
                milestone_id=milestone.id,
                status="paid",
                payment=MilestonePaymentRead(
                    status=existing_payment.status,
                    amount=existing_payment.amount,
                    mock_txn_ref=existing_payment.mock_txn_ref,
                    released_at=existing_payment.released_at,
                ),
            )

    # Gate: payment is blocked until validation
    if milestone.status != "validated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="milestone must be validated before payment",
        )

    # Mock payment generation per roadmap
    mock_txn_ref = f"MOCK-PAY-{milestone.id:04d}"
    milestone.status = "paid"

    payment = Payment(
        milestone_id=milestone.id,
        amount=milestone.amount,
        status="released",
        mock_txn_ref=mock_txn_ref,
        released_at=datetime.now(timezone.utc),
    )
    session.add(payment)
    session.add(milestone)
    session.commit()
    session.refresh(milestone)
    session.refresh(payment)

    return MilestonePayOut(
        milestone_id=milestone.id,
        status="paid",
        payment=MilestonePaymentRead(
            status=payment.status,
            amount=payment.amount,
            mock_txn_ref=payment.mock_txn_ref,
            released_at=payment.released_at,
        ),
    )
