from datetime import date,datetime
from typing import Optional
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password_hash: str
    role: str
    department: Optional[str] = None
    district: Optional[str] = None
class Startup(SQLModel, table=True):
    __tablename__ = "startups"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    name: str
    sector: str
    technologies: list = Field(default_factory=list, sa_type=JSON)
    tech_tags: list = Field(default_factory=list, sa_type=JSON)
    dpiit_number: Optional[str] = None
    incorporation_year: Optional[int] = None
    turnover: Optional[int] = None
    team_size: Optional[int] = None
    past_projects: list = Field(default_factory=list, sa_type=JSON)
    certifications: list = Field(default_factory=list, sa_type=JSON)
    description: Optional[str] = None
from datetime import date
class Challenge(SQLModel, table=True):
    __tablename__ = "challenges"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_by: int
    department: str
    district: str
    title: str
    raw_description: str
    statement_json: dict = Field(default_factory=dict, sa_type=JSON)
    sector: str
    required_tech: list = Field(default_factory=list, sa_type=JSON)
    eligibility_rules_json: dict = Field(default_factory=dict, sa_type=JSON)
    kpi_targets_json: dict = Field(default_factory=dict, sa_type=JSON)
    budget: Optional[int] = None
    timeline_days: Optional[int] = None
    deadline: Optional[date] = None
    status: str
    match_rubric_id: Optional[int] = None
    evaluation_rubric_id: Optional[int] = None
class Application(SQLModel, table=True):
    __tablename__ = "applications"

    id: Optional[int] = Field(default=None, primary_key=True)
    challenge_id: int
    startup_id: int
    eligible: bool = False
    eligibility_report_json: dict = Field(default_factory=dict, sa_type=JSON)
    match_score: Optional[float] = None
    match_breakdown_json: dict = Field(default_factory=dict, sa_type=JSON)
    rubric_snapshot_json: dict = Field(default_factory=dict, sa_type=JSON)
    explanation: Optional[str] = None
    status: str = "applied"
class Evaluation(SQLModel, table=True):
    __tablename__ = "evaluations"

    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int
    expert_id: int
    scores_json: dict = Field(default_factory=dict, sa_type=JSON)
    weighted_total: Optional[float] = None
    rubric_snapshot_json: dict = Field(default_factory=dict, sa_type=JSON)
    comments: Optional[str] = None
    submitted_at: Optional[datetime] = None
class Rubric(SQLModel, table=True):
    __tablename__ = "rubrics"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    kind: str
    weights_json: dict = Field(default_factory=dict, sa_type=JSON)
    criteria_json: dict = Field(default_factory=dict, sa_type=JSON)
    version: int = 1
    is_default: bool = False
    active: bool = True
    created_by: int
    created_at: Optional[datetime] = None
class Pilot(SQLModel, table=True):
    __tablename__ = "pilots"

    id: Optional[int] = Field(default=None, primary_key=True)
    challenge_id: int
    startup_id: int
    location: str
    duration_days: int
    budget: int
    objectives: str
    security_checklist_json: dict = Field(default_factory=dict, sa_type=JSON)
    security_status: str = "pending"
    risk_level: Optional[str] = None
    status: str
class Milestone(SQLModel, table=True):
    __tablename__ = "milestones"

    id: Optional[int] = Field(default=None, primary_key=True)
    pilot_id: int
    seq: int
    title: str
    deliverable: str
    amount: int 
    due_date: Optional[date] = None
    status: str = "pending"
    evidence_text: Optional[str] = None
    evidence_url: Optional[str] = None
    claimed_value: Optional[float] = None
    submitted_at: Optional[datetime] = None
class Validation(SQLModel, table=True):
    __tablename__ = "validations"

    id: Optional[int] = Field(default=None, primary_key=True)
    milestone_id: int
    validator_id: int
    claimed_value: Optional[float] = None
    verified_value: Optional[float] = None
    verdict: str
    evidence_notes: Optional[str] = None
    validated_at: Optional[datetime] = None
class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    milestone_id: int
    amount: int
    status: str
    released_at: Optional[datetime] = None
    mock_txn_ref: Optional[str] = None
class KPI(SQLModel, table=True):
    __tablename__ = "kpis"

    id: Optional[int] = Field(default=None, primary_key=True)
    pilot_id: int
    name: str
    unit: str
    baseline: Optional[float] = None
    target: Optional[float] = None
    achieved: Optional[float] = None
    met: bool = False
    category: str
    direction: str
class Risk(SQLModel, table=True):
    __tablename__ = "risks"

    id: Optional[int] = Field(default=None, primary_key=True)
    pilot_id: int
    description: str
    probability: int
    impact: int
    score: int
    mitigation: Optional[str] = None
    owner: Optional[str] = None
class Procurement(SQLModel, table=True):
    __tablename__ = "procurement"

    id: Optional[int] = Field(default=None, primary_key=True)
    pilot_id: int
    final_score: Optional[float] = None
    decision: str
    pathway: Optional[str] = None
    justification: Optional[str] = None
    replication_json: list = Field(default_factory=list, sa_type=JSON)
