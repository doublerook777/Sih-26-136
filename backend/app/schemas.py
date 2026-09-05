"""
Request and response schemas for ProcuraAI.
Every field name here matches docs/API.md exactly. This file exists specifically
to prevent DB column names (with the _json suffix) from leaking into API responses,
and to stop raw ORM objects (which would include password_hash) from being returned
directly to the client.
"""
from datetime import date, datetime
from typing import Literal, Optional

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


class GenerateStatementIn(BaseModel):
    raw_description: str
    title: str
    department: str
    district: str
    sector: str
    budget: int
    timeline_days: int


class GenerateStatementOut(BaseModel):
    problem: str
    background: str
    existing_system: str
    identified_gap: str
    desired_solution: str
    target_users: str
    technical_requirements: str
    constraints: str
    budget: str
    timeline: str
    expected_outcomes: str
    kpis: str
    eligibility_requirements: str
    data_requirements: str
    security_requirements: str
    generated_by: Literal["llm", "template"]


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
# Applications
# ---------------------------------------------------------------------------

class ApplicationCreate(BaseModel):
    challenge_id: int
    quote: int
    pitch: str

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


# ---------------------------------------------------------------------------
# Milestones, Validation, Payment (Pilots Sub-objects)
# ---------------------------------------------------------------------------

class MilestoneValidationRead(BaseModel):
    verdict: str
    claimed_value: Optional[float] = None
    verified_value: Optional[float] = None
    validator_name: Optional[str] = None
    notes: Optional[str] = None
    validated_at: Optional[datetime] = None


class MilestonePaymentRead(BaseModel):
    status: str
    amount: int
    mock_txn_ref: Optional[str] = None
    released_at: Optional[datetime] = None


class MilestoneRead(BaseModel):
    id: int
    seq: int
    title: str
    deliverable: str
    amount: int
    due_date: Optional[date] = None
    status: str
    evidence_text: Optional[str] = None
    evidence_url: Optional[str] = None
    claimed_value: Optional[float] = None
    submitted_at: Optional[datetime] = None
    validation: Optional[MilestoneValidationRead] = None
    payment: Optional[MilestonePaymentRead] = None


class MilestoneCreate(BaseModel):
    seq: int
    title: str
    deliverable: str
    amount: int
    due_date: Optional[date] = None


class MilestoneSubmitIn(BaseModel):
    evidence_text: str
    evidence_url: Optional[str] = None
    claimed_value: Optional[float] = None


class MilestoneSubmitOut(BaseModel):
    id: int
    status: str
    submitted_at: Optional[datetime] = None


class MilestoneValidateIn(BaseModel):
    verdict: str
    verified_value: Optional[float] = None
    notes: Optional[str] = None


class MilestoneValidateOut(BaseModel):
    milestone_id: int
    status: str
    validation: MilestoneValidationRead


class MilestonePayOut(BaseModel):
    milestone_id: int
    status: str
    payment: MilestonePaymentRead



# ---------------------------------------------------------------------------
# Governance: KPIs, Risks, Security
# ---------------------------------------------------------------------------

class KPICreate(BaseModel):
    name: str
    unit: str
    baseline: Optional[float] = None
    target: Optional[float] = None
    category: str
    direction: str


class KPIRead(BaseModel):
    id: int
    name: str
    unit: str
    baseline: Optional[float] = None
    target: Optional[float] = None
    achieved: Optional[float] = None
    category: str
    direction: str
    achievement: Optional[float] = None
    met: bool = False


class KPIUpdate(BaseModel):
    kpi_id: int
    achieved: float


class RiskCreate(BaseModel):
    description: str
    probability: int
    impact: int
    mitigation: Optional[str] = None
    owner: Optional[str] = None


class RiskRead(BaseModel):
    id: int
    description: str
    probability: int
    impact: int
    score: int
    mitigation: Optional[str] = None
    owner: Optional[str] = None


class SecurityCheckIn(BaseModel):
    authentication: bool
    authorization: bool
    data_encryption: bool
    secure_api: bool
    data_backup: bool
    vulnerability_assessment: bool
    access_logging: bool
    incident_response_plan: bool


class SecurityCheckOut(BaseModel):
    pilot_id: int
    security_status: str
    score: float
    passed_count: int
    total_count: int
    failed: list[str]


# ---------------------------------------------------------------------------
# Pilots
# ---------------------------------------------------------------------------

class PilotCreate(BaseModel):
    challenge_id: int
    startup_id: int
    location: str
    duration_days: int
    budget: int
    objectives: str
    milestones: list[MilestoneCreate]
    kpis: list[KPICreate]


class PilotSummary(BaseModel):
    id: int
    challenge_title: str
    startup_name: str
    location: str
    status: str
    budget: int
    paid_to_date: int
    milestones_total: int
    milestones_paid: int
    security_status: str
    risk_level: Optional[str] = None


class PilotDetail(BaseModel):
    id: int
    challenge_id: int
    challenge_title: str
    startup_id: int
    startup_name: str
    location: str
    duration_days: int
    budget: int
    paid_to_date: int
    status: str
    security_status: str
    risk_level: Optional[str] = None
    milestones: list[MilestoneRead]
    kpis: list[KPIRead]
    risks: list[RiskRead]
    security_checklist: dict


class PilotCreateResponse(BaseModel):
    id: int
    challenge_id: int
    startup_id: int
    startup_name: str
    location: str
    duration_days: int
    budget: int
    objectives: str
    status: str
    security_status: str
    risk_level: Optional[str] = None
    milestones: list[MilestoneRead]
    kpis: list[KPIRead]
    created_at: Optional[datetime] = None


class PilotFinalizeOut(BaseModel):
    pilot_id: int
    category_scores: dict[str, float]
    weights: dict[str, int]
    final_score: float
    decision: str
    justification: str


class ProcurementChecks(BaseModel):
    pilot_validated: bool
    performance_threshold_met: bool
    security_approved: bool
    budget_available: bool


class ReplicationItem(BaseModel):
    district: str
    status: str


class PilotProcurementOut(BaseModel):
    pilot_id: int
    final_score: Optional[float] = None
    decision: Optional[str] = None
    checks: ProcurementChecks
    recommended_pathway: str
    justification: Optional[str] = None
    replication: list[ReplicationItem]


class ReplicateIn(BaseModel):
    districts: list[str]


class ReplicateOut(BaseModel):
    pilot_id: int
    replication: list[ReplicationItem]


# ---------------------------------------------------------------------------
# Rubrics
# ---------------------------------------------------------------------------

class RubricCriterion(BaseModel):
    key: str
    label: str
    weight: float
    help: Optional[str] = None


class RubricRead(BaseModel):
    id: int
    name: str
    kind: str
    version: int
    is_default: bool
    active: bool
    weights: dict[str, float]
    criteria: list[RubricCriterion]


class RubricCreate(BaseModel):
    name: str
    kind: str
    criteria: list[RubricCriterion]


# ---------------------------------------------------------------------------
# Evaluations
# ---------------------------------------------------------------------------

class EvaluationCreate(BaseModel):
    application_id: int
    scores: dict[str, float]
    comments: Optional[str] = None


class EvaluationRead(BaseModel):
    id: int
    application_id: int
    expert_id: int
    expert_name: str
    scores: dict[str, float]
    weighted_total: float
    rubric_snapshot: dict[str, float]
    comments: Optional[str] = None
    submitted_at: Optional[datetime] = None


class EvaluationsListOut(BaseModel):
    application_id: int
    average_total: Optional[float] = None
    evaluation_count: int
    evaluations: list[EvaluationRead]


# ---------------------------------------------------------------------------
# Application status transitions
# ---------------------------------------------------------------------------

class ApplicationShortlistOut(BaseModel):
    application_id: int
    status: str


class ApplicationSelectOut(BaseModel):
    application_id: int
    status: str
    challenge_status: str


