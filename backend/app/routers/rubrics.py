from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import get_current_user, require_role
from app.db import get_session
from app.engines.rubric import validate_rubric
from app.models import Rubric, User
from app.schemas import RubricCreate, RubricRead

router = APIRouter(tags=["rubrics"])


def _rubric_read(rubric: Rubric) -> RubricRead:
    return RubricRead(
        id=rubric.id,
        name=rubric.name,
        kind=rubric.kind,
        version=rubric.version,
        is_default=rubric.is_default,
        active=rubric.active,
        weights=rubric.weights_json,
        criteria=rubric.criteria_json,
    )


@router.get("/rubrics", response_model=list[RubricRead])
def list_rubrics(
    kind: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(Rubric)
    if kind:
        query = query.where(Rubric.kind == kind)
    rubrics = session.exec(query).all()
    return [_rubric_read(r) for r in rubrics]


@router.get("/rubrics/{rubric_id}", response_model=RubricRead)
def get_rubric(
    rubric_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    rubric = session.get(Rubric, rubric_id)
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return _rubric_read(rubric)


def _create_rubric(session: Session, current_user: User, data: RubricCreate, version: int, is_default: bool) -> Rubric:
    weights = {c.key: c.weight for c in data.criteria}
    try:
        validate_rubric(weights, data.kind)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    rubric = Rubric(
        name=data.name,
        kind=data.kind,
        weights_json=weights,
        criteria_json=[c.model_dump() for c in data.criteria],
        version=version,
        is_default=is_default,
        active=True,
        created_by=current_user.id,
        created_at=datetime.now(timezone.utc),
    )
    session.add(rubric)
    session.commit()
    session.refresh(rubric)
    return rubric


@router.post("/rubrics", response_model=RubricRead, status_code=201)
def create_rubric(
    data: RubricCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
):
    rubric = _create_rubric(session, current_user, data, version=1, is_default=False)
    return _rubric_read(rubric)


@router.post("/rubrics/{rubric_id}/clone", response_model=RubricRead, status_code=201)
def clone_rubric(
    rubric_id: int,
    data: RubricCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
):
    original = session.get(Rubric, rubric_id)
    if not original:
        raise HTTPException(status_code=404, detail="Rubric not found")

    # The only way to "edit" a used rubric — the original row is left untouched.
    rubric = _create_rubric(
        session, current_user, data, version=original.version + 1, is_default=False
    )
    return _rubric_read(rubric)
