from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import require_role
from app.db import get_session
from app.engines.evaluation import average_evaluations, score_evaluation
from app.models import Application, Challenge, Evaluation, User
from app.schemas import EvaluationCreate, EvaluationRead, EvaluationsListOut
from app.scoring import resolve_rubric

router = APIRouter(tags=["evaluations"])


def _evaluation_read(session: Session, evaluation: Evaluation) -> EvaluationRead:
    expert = session.get(User, evaluation.expert_id)
    return EvaluationRead(
        id=evaluation.id,
        application_id=evaluation.application_id,
        expert_id=evaluation.expert_id,
        expert_name=expert.name if expert else "Unknown expert",
        scores=evaluation.scores_json,
        weighted_total=evaluation.weighted_total,
        rubric_snapshot=evaluation.rubric_snapshot_json,
        comments=evaluation.comments,
        submitted_at=evaluation.submitted_at,
    )


@router.post("/evaluations", response_model=EvaluationRead, status_code=201)
def create_evaluation(
    data: EvaluationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("expert")),
):
    application = session.get(Application, data.application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    challenge = session.get(Challenge, application.challenge_id)
    rubric = resolve_rubric(session, challenge.evaluation_rubric_id if challenge else None, "evaluation")
    if not rubric:
        raise HTTPException(status_code=400, detail="No evaluation rubric is configured for this challenge")

    try:
        result = score_evaluation(data.scores, rubric.weights_json)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    evaluation = Evaluation(
        application_id=application.id,
        expert_id=current_user.id,
        scores_json=data.scores,
        weighted_total=result["weighted_total"],
        rubric_snapshot_json=result["rubric_snapshot"],
        comments=data.comments,
        submitted_at=datetime.now(timezone.utc),
    )
    session.add(evaluation)

    application.status = "evaluated"
    session.add(application)

    session.commit()
    session.refresh(evaluation)
    return _evaluation_read(session, evaluation)


@router.get("/evaluations", response_model=EvaluationsListOut)
def list_evaluations(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("government", "expert")),
):
    evaluations = session.exec(
        select(Evaluation).where(Evaluation.application_id == application_id)
    ).all()
    summary = average_evaluations(evaluations)

    return EvaluationsListOut(
        application_id=application_id,
        average_total=summary["average_total"],
        evaluation_count=summary["evaluation_count"],
        evaluations=[_evaluation_read(session, e) for e in evaluations],
    )
