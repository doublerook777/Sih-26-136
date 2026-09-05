from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import get_current_user
from app.db import get_session
from app.models import Startup, User
from app.schemas import StartupRead

router = APIRouter(tags=["startups"])


@router.get("/startups", response_model=list[StartupRead])
def list_startups(
    sector: Optional[str] = None,
    tech: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(Startup)
    if sector:
        query = query.where(Startup.sector == sector.lower())

    startups = session.exec(query).all()

    if tech:
        # filter on tech_tags, never the free-text technologies field —
        # technologies has ~94 unique phrases across 20 startups and
        # filtering on it returns almost nothing
        startups = [s for s in startups if tech.lower() in [t.lower() for t in s.tech_tags]]

    return startups


@router.get("/startups/{startup_id}", response_model=StartupRead)
def get_startup(
    startup_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    startup = session.get(Startup, startup_id)
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    return startup
