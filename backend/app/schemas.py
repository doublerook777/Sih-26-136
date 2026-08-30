"""
Request and response schemas for ProcuraAI.
Every field name here matches docs/API.md exactly. This file exists specifically
to prevent DB column names (with the _json suffix) from leaking into API responses,
and to stop raw ORM objects (which would include password_hash) from being returned
directly to the client.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str
    department: Optional[str] = None
    district: Optional[str] = None


class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    email: str
    role: str
    department: Optional[str] = None
    district: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: UserRead


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------

class ChallengeListItem(BaseModel):
    id: int
    title: str
    department: str
    district: str
    sector: str
    budget: Optional[int] = None
    timeline_days: Optional[int] = None
    deadline: Optional[date] = None
    status: str
    required_tech: list
    application_count: int
    created_at: Optional[datetime] = None
    raw_description: str  # added beyond the original 11 fields: Pair B's search needs it


class ChallengeDetail(BaseModel):
    id: int
    title: str
    department: str
    district: str
    sector: str
    budget: Optional[int] = None
    timeline_days: Optional[int] = None
    deadline: Optional[date] = None
    status: str
    required_tech: list
    application_count: int
    created_at: Optional[datetime] = None
    raw_description: str
    created_by: int
    match_rubric_id: Optional[int] = None
    evaluation_rubric_id: Optional[int] = None
    # these three are read from Challenge.*_json columns but returned without
    # the suffix, per docs/API.md. See routers/challenges.py for the mapping.
    statement: dict
    eligibility_rules: dict
    kpi_targets: list


class ChallengeCreate(BaseModel):
    title: str
    raw_description: str
    department: str
    district: str
    sector: str
    budget: int
    timeline_days: int
    deadline: date
    required_tech: list
    match_rubric_id: Optional[int] = None
    evaluation_rubric_id: Optional[int] = None
    eligibility_rules: dict
    kpi_targets: list
    statement: Optional[dict] = None  # officer-approved statement from generate-statement


# ---------------------------------------------------------------------------
# Startups
# ---------------------------------------------------------------------------

class StartupRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    sector: str
    technologies: list
    tech_tags: list
    dpiit_number: Optional[str] = None
    incorporation_year: Optional[int] = None
    team_size: Optional[int] = None
    certifications: list
    description: Optional[str] = None
    past_projects: list


# ---------------------------------------------------------------------------
# Applications (read-only today; POST /applications is a later task)
# ---------------------------------------------------------------------------

class ApplicationRead(BaseModel):
    application_id: int
    startup_id: int
    startup_name: str
    eligible: bool
    eligibility_report: dict
    match_score: Optional[float] = None
    match_breakdown: dict
    rubric_snapshot: dict
    explanation: Optional[str] = None
    status: str
