import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.auth import create_access_token, hash_password
from app.db import get_session
from app.main import app
from app.models import Challenge, Milestone, Payment, Pilot, Startup, User, Validation
from app.schemas import (
    MilestoneRead,
    PilotCreate,
    PilotDetail,
    PilotSummary,
    SecurityCheckIn,
    SecurityCheckOut,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="seed_entities")
def seed_entities_fixture(session: Session):
    # Create users
    gov_user = User(
        id=1,
        name="R Kumar",
        email="gov@water.gov.in",
        password_hash=hash_password("secret123"),
        role="government",
        department="Urban Water Supply",
        district="District A",
    )
    startup_user_1 = User(
        id=2,
        name="Startup One User",
        email="user1@aquasense.in",
        password_hash=hash_password("secret123"),
        role="startup",
    )
    startup_user_2 = User(
        id=3,
        name="Startup Two User",
        email="user2@other.in",
        password_hash=hash_password("secret123"),
        role="startup",
    )
    validator_user = User(
        id=4,
        name="N Sharma",
        email="validator@water.gov.in",
        password_hash=hash_password("secret123"),
        role="validator",
    )
    session.add_all([gov_user, startup_user_1, startup_user_2, validator_user])
    session.commit()

    # Create startups
    startup_1 = Startup(
        id=1,
        user_id=2,
        name="AquaSense",
        sector="water",
        technologies=["IoT", "Acoustic Sensors"],
    )
    startup_2 = Startup(
        id=2,
        user_id=3,
        name="OtherStartup",
        sector="water",
        technologies=["GIS"],
    )
    session.add_all([startup_1, startup_2])

    # Create challenge
    challenge = Challenge(
        id=1,
        created_by=1,
        department="Urban Water Supply",
        district="District A",
        title="Reduce municipal water leakage",
        raw_description="A test challenge",
        sector="water",
        required_tech=["IoT"],
        status="open",
        budget=1000000,
        timeline_days=90,
    )
    session.add(challenge)
    session.commit()

    return {
        "gov_token": create_access_token(1),
        "startup_1_token": create_access_token(2),
        "startup_2_token": create_access_token(3),
        "validator_token": create_access_token(4),
        "challenge_id": 1,
        "startup_1_id": 1,
        "startup_2_id": 2,
    }


# ===========================================================================
# CHECKPOINT 1: Schemas
# ===========================================================================

def test_checkpoint1_schemas_nullability_and_types():
    # MilestoneRead validation and payment default to None
    m = MilestoneRead(
        id=1,
        seq=1,
        title="Prototype",
        deliverable="Sensor kit",
        amount=200000,
        status="pending",
    )
    assert m.validation is None
    assert m.payment is None
    assert isinstance(m.amount, int)

    # SecurityCheckIn requires the 8 boolean fields
    sec_in = SecurityCheckIn(
        authentication=True,
        authorization=True,
        data_encryption=True,
        secure_api=True,
        data_backup=True,
        vulnerability_assessment=True,
        access_logging=True,
        incident_response_plan=False,
    )
    assert sec_in.incident_response_plan is False

    # SecurityCheckOut shape
    sec_out = SecurityCheckOut(
        pilot_id=1,
        security_status="needs_remediation",
        score=87.5,
        passed_count=7,
        total_count=8,
        failed=["incident_response_plan"],
    )
    assert sec_out.score == 87.5
    assert sec_out.failed == ["incident_response_plan"]


# ===========================================================================
# CHECKPOINT 2: POST /pilots (Create pilot + 4 milestones + KPIs in one call)
# ===========================================================================

def test_checkpoint2_create_pilot_budget_mismatch_fails_400(client, seed_entities, session: Session):
    headers = {"Authorization": f"Bearer {seed_entities['gov_token']}"}
    payload = {
        "challenge_id": seed_entities["challenge_id"],
        "startup_id": seed_entities["startup_1_id"],
        "location": "District A",
        "duration_days": 90,
        "budget": 1000000,
        "objectives": "Reduce water loss",
        "milestones": [
            {"seq": 1, "title": "M1", "deliverable": "D1", "amount": 200000, "due_date": "2026-09-20"},
            {"seq": 2, "title": "M2", "deliverable": "D2", "amount": 300000, "due_date": "2026-10-10"},
            {"seq": 3, "title": "M3", "deliverable": "D3", "amount": 300000, "due_date": "2026-11-01"},
            {"seq": 4, "title": "M4", "deliverable": "D4", "amount": 100000, "due_date": "2026-11-25"},  # sums to 900,000 != 1,000,000
        ],
        "kpis": [
            {"name": "Water wastage", "unit": "%", "baseline": 30, "target": 20, "category": "impact", "direction": "lower_is_better"}
        ],
    }
    response = client.post("/pilots", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Milestone amounts must sum to the pilot budget"

    # Confirm no rows were created in DB
    pilots = session.exec(select(Pilot)).all()
    assert len(pilots) == 0
    milestones = session.exec(select(Milestone)).all()
    assert len(milestones) == 0


def test_checkpoint2_create_pilot_valid_success(client, seed_entities, session: Session):
    headers = {"Authorization": f"Bearer {seed_entities['gov_token']}"}
    payload = {
        "challenge_id": seed_entities["challenge_id"],
        "startup_id": seed_entities["startup_1_id"],
        "location": "District A",
        "duration_days": 90,
        "budget": 1000000,
        "objectives": "Reduce water loss by 10%",
        "milestones": [
            {"seq": 1, "title": "Prototype", "deliverable": "Sensor kit", "amount": 200000, "due_date": "2026-09-20"},
            {"seq": 2, "title": "Field trial", "deliverable": "Live trial", "amount": 300000, "due_date": "2026-10-10"},
            {"seq": 3, "title": "Deployment", "deliverable": "Full coverage", "amount": 300000, "due_date": "2026-11-01"},
            {"seq": 4, "title": "Final results", "deliverable": "Verified report", "amount": 200000, "due_date": "2026-11-25"},
        ],
        "kpis": [
            {"name": "Water wastage", "unit": "%", "baseline": 30, "target": 20, "category": "impact", "direction": "lower_is_better"},
            {"name": "System uptime", "unit": "%", "baseline": 0, "target": 95, "category": "technical", "direction": "higher_is_better"},
        ],
    }
    response = client.post("/pilots", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "created"
    assert data["security_status"] == "pending"
    assert data["risk_level"] is None
    assert data["startup_name"] == "AquaSense"
    assert len(data["milestones"]) == 4
    assert len(data["kpis"]) == 2

    # Check that validation and payment are null
    for m in data["milestones"]:
        assert m["validation"] is None
        assert m["payment"] is None
        assert m["status"] == "pending"


# ===========================================================================
# CHECKPOINT 3: GET /pilots and GET /pilots/{id}
# ===========================================================================

def test_checkpoint3_get_pilots_list_and_detail(client, seed_entities, session: Session):
    headers_gov = {"Authorization": f"Bearer {seed_entities['gov_token']}"}
    headers_startup_1 = {"Authorization": f"Bearer {seed_entities['startup_1_token']}"}
    headers_startup_2 = {"Authorization": f"Bearer {seed_entities['startup_2_token']}"}

    # Create a pilot for startup 1
    payload = {
        "challenge_id": seed_entities["challenge_id"],
        "startup_id": seed_entities["startup_1_id"],
        "location": "District A",
        "duration_days": 90,
        "budget": 1000000,
        "objectives": "Reduce water loss",
        "milestones": [
            {"seq": 1, "title": "Prototype", "deliverable": "Sensor kit", "amount": 200000, "due_date": "2026-09-20"},
            {"seq": 2, "title": "Field trial", "deliverable": "Live trial", "amount": 300000, "due_date": "2026-10-10"},
            {"seq": 3, "title": "Deployment", "deliverable": "Full coverage", "amount": 300000, "due_date": "2026-11-01"},
            {"seq": 4, "title": "Final results", "deliverable": "Verified report", "amount": 200000, "due_date": "2026-11-25"},
        ],
        "kpis": [
            {"name": "Water wastage", "unit": "%", "baseline": 30, "target": 20, "category": "impact", "direction": "lower_is_better"}
        ],
    }
    create_res = client.post("/pilots", json=payload, headers=headers_gov)
    pilot_id = create_res.json()["id"]

    # Test GET /pilots summary list
    list_res = client.get("/pilots", headers=headers_gov)
    assert list_res.status_code == 200
    summaries = list_res.json()
    assert len(summaries) == 1
    assert summaries[0]["id"] == pilot_id
    assert summaries[0]["challenge_title"] == "Reduce municipal water leakage"
    assert summaries[0]["startup_name"] == "AquaSense"
    assert summaries[0]["paid_to_date"] == 0
    assert summaries[0]["milestones_total"] == 4
    assert summaries[0]["milestones_paid"] == 0
    assert "milestones" not in summaries[0]  # Flatter summary shape

    # Test GET /pilots/{id} detail
    detail_res = client.get(f"/pilots/{pilot_id}", headers=headers_gov)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["paid_to_date"] == 0
    assert len(detail["milestones"]) == 4
    assert detail["milestones"][0]["validation"] is None
    assert detail["milestones"][0]["payment"] is None

    # Test Access Control: Startup 1 can view their own pilot
    st1_res = client.get(f"/pilots/{pilot_id}", headers=headers_startup_1)
    assert st1_res.status_code == 200

    # Test Access Control: Startup 2 CANNOT view Startup 1's pilot (403)
    st2_res = client.get(f"/pilots/{pilot_id}", headers=headers_startup_2)
    assert st2_res.status_code == 403

    # Startup 2 listing pilots only sees their own (which is empty)
    st2_list = client.get("/pilots", headers=headers_startup_2)
    assert st2_list.status_code == 200
    assert len(st2_list.json()) == 0

    # Simulate paid milestone and verify paid_to_date updates
    first_milestone = session.exec(select(Milestone)).first()
    first_milestone.status = "paid"
    payment = Payment(
        milestone_id=first_milestone.id,
        amount=200000,
        status="released",
        mock_txn_ref="MOCK-PAY-0001",
    )
    session.add(payment)
    session.add(first_milestone)
    session.commit()

    detail_after_pay = client.get(f"/pilots/{pilot_id}", headers=headers_gov).json()
    assert detail_after_pay["paid_to_date"] == 200000
    assert detail_after_pay["milestones"][0]["payment"]["status"] == "released"
    assert detail_after_pay["milestones"][0]["payment"]["amount"] == 200000


# ===========================================================================
# CHECKPOINT 4: POST /pilots/{id}/security-check
# ===========================================================================

def test_checkpoint4_security_check(client, seed_entities):
    headers_gov = {"Authorization": f"Bearer {seed_entities['gov_token']}"}

    # Create pilot
    payload = {
        "challenge_id": seed_entities["challenge_id"],
        "startup_id": seed_entities["startup_1_id"],
        "location": "District A",
        "duration_days": 90,
        "budget": 1000000,
        "objectives": "Reduce water loss",
        "milestones": [
            {"seq": 1, "title": "M1", "deliverable": "D1", "amount": 1000000, "due_date": "2026-09-20"},
        ],
        "kpis": [
            {"name": "Water wastage", "unit": "%", "baseline": 30, "target": 20, "category": "impact", "direction": "lower_is_better"}
        ],
    }
    pilot_id = client.post("/pilots", json=payload, headers=headers_gov).json()["id"]

    # 1. Test 7 true, 1 false -> score 87.5, needs_remediation
    check_payload_fail = {
        "authentication": True,
        "authorization": True,
        "data_encryption": True,
        "secure_api": True,
        "data_backup": True,
        "vulnerability_assessment": True,
        "access_logging": True,
        "incident_response_plan": False,
    }
    res_fail = client.post(f"/pilots/{pilot_id}/security-check", json=check_payload_fail, headers=headers_gov)
    assert res_fail.status_code == 200
    data_fail = res_fail.json()
    assert data_fail["security_status"] == "needs_remediation"
    assert data_fail["score"] == 87.5
    assert data_fail["passed_count"] == 7
    assert data_fail["total_count"] == 8
    assert data_fail["failed"] == ["incident_response_plan"]

    # Verify pilot's stored security_status updated via GET /pilots/{id}
    detail_res = client.get(f"/pilots/{pilot_id}", headers=headers_gov).json()
    assert detail_res["security_status"] == "needs_remediation"
    assert detail_res["security_checklist"]["incident_response_plan"] is False

    # 2. Test all 8 true -> score 100.0, passed
    check_payload_pass = {
        "authentication": True,
        "authorization": True,
        "data_encryption": True,
        "secure_api": True,
        "data_backup": True,
        "vulnerability_assessment": True,
        "access_logging": True,
        "incident_response_plan": True,
    }
    res_pass = client.post(f"/pilots/{pilot_id}/security-check", json=check_payload_pass, headers=headers_gov)
    assert res_pass.status_code == 200
    data_pass = res_pass.json()
    assert data_pass["security_status"] == "passed"
    assert data_pass["score"] == 100.0
    assert data_pass["passed_count"] == 8
    assert data_pass["failed"] == []

    # Verify pilot's stored security_status updated via GET /pilots/{id}
    detail_pass = client.get(f"/pilots/{pilot_id}", headers=headers_gov).json()
    assert detail_pass["security_status"] == "passed"


# ===========================================================================
# CHECKPOINT 5: GET/POST /pilots/{id}/risks and /kpis
# ===========================================================================

def test_checkpoint5_risks_and_kpis(client, seed_entities):
    headers_gov = {"Authorization": f"Bearer {seed_entities['gov_token']}"}

    # Create pilot
    payload = {
        "challenge_id": seed_entities["challenge_id"],
        "startup_id": seed_entities["startup_1_id"],
        "location": "District A",
        "duration_days": 90,
        "budget": 1000000,
        "objectives": "Reduce water loss",
        "milestones": [
            {"seq": 1, "title": "M1", "deliverable": "D1", "amount": 1000000, "due_date": "2026-09-20"},
        ],
        "kpis": [
            {"name": "Water wastage", "unit": "%", "baseline": 30, "target": 20, "category": "impact", "direction": "lower_is_better"},
            {"name": "System uptime", "unit": "%", "baseline": 0, "target": 95, "category": "technical", "direction": "higher_is_better"},
        ],
    }
    pilot_id = client.post("/pilots", json=payload, headers=headers_gov).json()["id"]

    # 1. Verify GET /pilots/{id}/kpis before any measurement shows achieved: null, achievement: null
    kpis_init = client.get(f"/pilots/{pilot_id}/kpis", headers=headers_gov).json()
    assert len(kpis_init) == 2
    for k in kpis_init:
        assert k["achieved"] is None
        assert k["achievement"] is None
        assert k["met"] is False

    # 2. Add risk with probability 3, impact 4 -> score 12, medium risk
    risk_payload = {
        "description": "Sensor failure in monsoon",
        "probability": 3,
        "impact": 4,
        "mitigation": "Ship 10% spare nodes",
        "owner": "AquaSense",
    }
    risk_res = client.post(f"/pilots/{pilot_id}/risks", json=risk_payload, headers=headers_gov)
    assert risk_res.status_code == 201
    risk_data = risk_res.json()
    assert risk_data["score"] == 12

    # Check pilot.risk_level updated to 'medium'
    pilot_detail = client.get(f"/pilots/{pilot_id}", headers=headers_gov).json()
    assert pilot_detail["risk_level"] == "medium"

    # Add high risk (probability 4, impact 4 -> score 16 -> 'high')
    high_risk_payload = {
        "description": "Critical supplier bankruptcy",
        "probability": 4,
        "impact": 4,
        "mitigation": "Dual vendor sourcing",
        "owner": "Gov",
    }
    risk_res2 = client.post(f"/pilots/{pilot_id}/risks", json=high_risk_payload, headers=headers_gov)
    assert risk_res2.status_code == 201
    assert risk_res2.json()["score"] == 16

    pilot_detail2 = client.get(f"/pilots/{pilot_id}", headers=headers_gov).json()
    assert pilot_detail2["risk_level"] == "high"

    # Test GET /pilots/{id}/risks
    risks_list = client.get(f"/pilots/{pilot_id}/risks", headers=headers_gov).json()
    assert len(risks_list) == 2

    # 3. Update KPI 1 (lower_is_better: baseline 30, target 20, achieved 17 -> capped at 120.0, met: True)
    kpi1_id = kpis_init[0]["id"]
    kpi1_update = client.post(
        f"/pilots/{pilot_id}/kpis",
        json={"kpi_id": kpi1_id, "achieved": 17},
        headers=headers_gov,
    )
    assert kpi1_update.status_code == 200
    k1 = kpi1_update.json()
    assert k1["achieved"] == 17.0
    assert k1["achievement"] == 120.0
    assert k1["met"] is True

    # 4. Update KPI 2 (higher_is_better: baseline 0, target 95, achieved 90 -> 90/95*100 = 94.7%, met: False)
    kpi2_id = kpis_init[1]["id"]
    kpi2_update = client.post(
        f"/pilots/{pilot_id}/kpis",
        json={"kpi_id": kpi2_id, "achieved": 90},
        headers=headers_gov,
    )
    assert kpi2_update.status_code == 200
    k2 = kpi2_update.json()
    assert k2["achieved"] == 90.0
    assert k2["achievement"] == 94.7
    assert k2["met"] is False
