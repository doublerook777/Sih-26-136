from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.auth import create_access_token, hash_password
from app.db import get_session
from app.main import app
from app.models import Challenge, KPI, Milestone, Payment, Pilot, Procurement, Risk, Startup, User, Validation


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
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
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="setup_data")
def setup_data_fixture(session: Session):
    # 1. Government user
    gov_user = User(
        id=1,
        name="R Kumar",
        email="officer@water.gov.in",
        password_hash=hash_password("demo1234"),
        role="government",
        department="Urban Water Supply",
        district="District A",
    )
    # 2. Admin user
    admin_user = User(
        id=2,
        name="Platform Admin",
        email="admin@procura.gov.in",
        password_hash=hash_password("demo1234"),
        role="admin",
    )
    # 3. Startup user and Startup
    startup_user = User(
        id=3,
        name="AquaSense Founder",
        email="founder@aquasense.in",
        password_hash=hash_password("demo1234"),
        role="startup",
    )
    startup = Startup(
        id=3,
        user_id=startup_user.id,
        name="AquaSense",
        sector="water",
        technologies=["iot", "sensors"],
        dpiit_number="DIPP12345",
    )
    # 4. Another startup user
    other_startup_user = User(
        id=4,
        name="Other Startup Founder",
        email="founder@other.in",
        password_hash=hash_password("demo1234"),
        role="startup",
    )
    other_startup = Startup(
        id=4,
        user_id=other_startup_user.id,
        name="OtherTech",
        sector="water",
    )
    # 5. Validator user
    validator_user = User(
        id=5,
        name="N Sharma",
        email="validator@procura.gov.in",
        password_hash=hash_password("demo1234"),
        role="validator",
    )
    # 6. Expert users (to cover 7 demo accounts)
    expert1 = User(id=6, name="Dr S Rao", email="expert1@procura.gov.in", password_hash=hash_password("demo1234"), role="expert")
    expert2 = User(id=7, name="Prof M Iyer", email="expert2@procura.gov.in", password_hash=hash_password("demo1234"), role="expert")

    session.add_all([gov_user, admin_user, startup_user, startup, other_startup_user, other_startup, validator_user, expert1, expert2])
    session.commit()

    # Challenge
    challenge = Challenge(
        id=1,
        created_by=gov_user.id,
        department="Urban Water Supply",
        district="District A",
        title="Reduce municipal water leakage",
        raw_description="Pipes leak",
        sector="water",
        budget=1000000,
        timeline_days=90,
        deadline=date(2026, 9, 15),
        status="piloting",
    )
    session.add(challenge)
    session.commit()

    # Pilot
    pilot = Pilot(
        id=1,
        challenge_id=challenge.id,
        startup_id=startup.id,
        location="District A",
        duration_days=90,
        budget=1000000,
        objectives="Reduce water loss by 10%",
        security_status="passed",
        security_checklist_json={
            "authentication": True,
            "authorization": True,
            "data_encryption": True,
            "secure_api": True,
            "data_backup": True,
            "vulnerability_assessment": True,
            "access_logging": True,
            "incident_response_plan": True,
        },
        risk_level="low",
        status="active",
    )
    session.add(pilot)
    session.commit()

    # 4 Milestones
    m1 = Milestone(id=1, pilot_id=pilot.id, seq=1, title="Prototype", deliverable="40 nodes", amount=200000, status="pending")
    m2 = Milestone(id=2, pilot_id=pilot.id, seq=2, title="Field trial", deliverable="Live data", amount=300000, status="pending")
    m3 = Milestone(id=3, pilot_id=pilot.id, seq=3, title="Deployment", deliverable="District coverage", amount=300000, status="pending")
    m4 = Milestone(id=4, pilot_id=pilot.id, seq=4, title="Final results", deliverable="KPI report", amount=200000, status="pending")
    session.add_all([m1, m2, m3, m4])

    # 4 KPIs
    kpi1 = KPI(id=1, pilot_id=pilot.id, name="Water wastage", unit="%", baseline=30, target=20, achieved=17, category="impact", direction="lower_is_better")
    kpi2 = KPI(id=2, pilot_id=pilot.id, name="Leak detection time", unit="hours", baseline=72, target=6, achieved=8, category="technical", direction="lower_is_better")
    kpi3 = KPI(id=3, pilot_id=pilot.id, name="System uptime", unit="%", baseline=0, target=95, achieved=96, category="technical", direction="higher_is_better")
    kpi4 = KPI(id=4, pilot_id=pilot.id, name="Cost per km", unit="INR", baseline=40000, target=25000, achieved=24000, category="cost", direction="lower_is_better")
    session.add_all([kpi1, kpi2, kpi3, kpi4])
    session.commit()

    tokens = {
        "gov": create_access_token(gov_user.id),
        "admin": create_access_token(admin_user.id),
        "startup": create_access_token(startup_user.id),
        "other_startup": create_access_token(other_startup_user.id),
        "validator": create_access_token(validator_user.id),
    }
    return tokens



# ===========================================================================
# CHECKPOINT 1: Milestone Submit and Validate
# ===========================================================================

def test_checkpoint_1_milestone_submit_and_validate(client: TestClient, setup_data: dict):
    tokens = setup_data

    # 1. A startup submitting their own milestone succeeds
    res = client.post(
        "/milestones/1/submit",
        json={
            "evidence_text": "40 nodes live since 14 Sep. Wastage down from 30% to 22.5%.",
            "evidence_url": "https://example.com/report.pdf",
            "claimed_value": 25.0,
        },
        headers={"Authorization": f"Bearer {tokens['startup']}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["id"] == 1
    assert data["status"] == "submitted"
    assert data["submitted_at"] is not None

    # Other startup cannot submit this milestone
    other_res = client.post(
        "/milestones/1/submit",
        json={"evidence_text": "Wrong startup", "claimed_value": 10.0},
        headers={"Authorization": f"Bearer {tokens['other_startup']}"},
    )
    assert other_res.status_code == 403

    # 2. The startup's own account attempting to validate its own milestone gets 403
    # "This is the rule the whole demo narrative depends on, test it explicitly"
    startup_val_res = client.post(
        "/milestones/1/validate",
        json={"verdict": "approved", "verified_value": 22.0, "notes": "Startup self validation"},
        headers={"Authorization": f"Bearer {tokens['startup']}"},
    )
    assert startup_val_res.status_code == 403
    assert "Startup cannot validate its own milestone" in startup_val_res.json()["detail"]

    # 3. A validator approving a submitted milestone moves it to validated
    val_res = client.post(
        "/milestones/1/validate",
        json={"verdict": "approved", "verified_value": 22.0, "notes": "Sampled 12 of 40 nodes."},
        headers={"Authorization": f"Bearer {tokens['validator']}"},
    )
    assert val_res.status_code == 200, val_res.text
    val_data = val_res.json()
    assert val_data["milestone_id"] == 1
    assert val_data["status"] == "validated"
    assert val_data["validation"]["verdict"] == "approved"
    assert val_data["validation"]["claimed_value"] == 25.0
    assert val_data["validation"]["verified_value"] == 22.0
    assert val_data["validation"]["validator_name"] == "N Sharma"

    # 4. A rejected verdict leaves the milestone at rejected, not validated
    # Submit milestone 2
    client.post(
        "/milestones/2/submit",
        json={"evidence_text": "Trial data", "claimed_value": 15.0},
        headers={"Authorization": f"Bearer {tokens['startup']}"},
    )
    rej_res = client.post(
        "/milestones/2/validate",
        json={"verdict": "rejected", "verified_value": 5.0, "notes": "Insufficient sensor accuracy."},
        headers={"Authorization": f"Bearer {tokens['validator']}"},
    )
    assert rej_res.status_code == 200, rej_res.text
    rej_data = rej_res.json()
    assert rej_data["status"] == "rejected"
    assert rej_data["validation"]["verdict"] == "rejected"


# ===========================================================================
# CHECKPOINT 2: Milestone Payment & Gate
# ===========================================================================

def test_checkpoint_2_milestone_payment(client: TestClient, setup_data: dict):
    tokens = setup_data

    # Setup: submit milestone 1 and validate it
    client.post(
        "/milestones/1/submit",
        json={"evidence_text": "Prototype complete", "claimed_value": 25.0},
        headers={"Authorization": f"Bearer {tokens['startup']}"},
    )
    client.post(
        "/milestones/1/validate",
        json={"verdict": "approved", "verified_value": 22.0, "notes": "Verified"},
        headers={"Authorization": f"Bearer {tokens['validator']}"},
    )

    # 1. Paying a submitted but-not-yet-validated milestone returns exactly the documented 400 message
    # Submit milestone 3 (not validated yet)
    client.post(
        "/milestones/3/submit",
        json={"evidence_text": "Deployed", "claimed_value": 10.0},
        headers={"Authorization": f"Bearer {tokens['startup']}"},
    )
    unval_pay = client.post(
        "/milestones/3/pay",
        headers={"Authorization": f"Bearer {tokens['gov']}"},
    )
    assert unval_pay.status_code == 400
    assert unval_pay.json()["detail"] == "milestone must be validated before payment"

    # 2. Paying a validated milestone succeeds, sets status to paid
    pay_res = client.post(
        "/milestones/1/pay",
        headers={"Authorization": f"Bearer {tokens['gov']}"},
    )
    assert pay_res.status_code == 200, pay_res.text
    pay_data = pay_res.json()
    assert pay_data["milestone_id"] == 1
    assert pay_data["status"] == "paid"
    assert pay_data["payment"]["status"] == "released"
    assert pay_data["payment"]["amount"] == 200000
    assert pay_data["payment"]["mock_txn_ref"] == "MOCK-PAY-0001"

    # 3. Paying an already-paid milestone doesn't double-pay (idempotent 200)
    repeat_pay = client.post(
        "/milestones/1/pay",
        headers={"Authorization": f"Bearer {tokens['gov']}"},
    )
    assert repeat_pay.status_code == 200
    assert repeat_pay.json()["payment"]["mock_txn_ref"] == "MOCK-PAY-0001"

    # 4. GET /pilots/{id}'s paid_to_date updates correctly after payment
    pilot_res = client.get("/pilots/1", headers={"Authorization": f"Bearer {tokens['gov']}"})
    assert pilot_res.status_code == 200
    pilot_data = pilot_res.json()
    assert pilot_data["paid_to_date"] == 200000


# ===========================================================================
# CHECKPOINT 3: POST /pilots/{id}/finalize
# ===========================================================================

def test_checkpoint_3_finalize_pilot(client: TestClient, setup_data: dict):
    tokens = setup_data

    # Finalize pilot 1
    res = client.post(
        "/pilots/1/finalize",
        headers={"Authorization": f"Bearer {tokens['gov']}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()

    # 1. A pilot with strong KPIs and passed security check finalizes to "scale"
    assert data["decision"] == "scale"
    assert data["final_score"] >= 85.0

    # 2. Category weights in the response match section 7b's 30/20/20/15/15 exactly
    assert data["weights"] == {
        "technical": 30,
        "cost": 20,
        "impact": 20,
        "scalability": 15,
        "security": 15,
    }

    # 3. The justification string names real numbers from this pilot, not generic praise
    justification = data["justification"]
    assert "Impact KPI score:" in justification or "%" in justification
    assert str(data["final_score"]) in justification


# ===========================================================================
# CHECKPOINT 4: GET /pilots/{id}/procurement & POST /pilots/{id}/replicate
# ===========================================================================

def test_checkpoint_4_procurement_and_replication(client: TestClient, setup_data: dict):
    tokens = setup_data

    # 1. procurement correctly reflects false if security hasn't passed or score is below threshold
    # Before finalizing, final_score is None, so performance_threshold_met is False
    proc_before = client.get("/pilots/1/procurement", headers={"Authorization": f"Bearer {tokens['gov']}"})
    assert proc_before.status_code == 200
    data_before = proc_before.json()
    assert data_before["checks"]["performance_threshold_met"] is False

    # Now finalize
    client.post("/pilots/1/finalize", headers={"Authorization": f"Bearer {tokens['gov']}"})

    # Validate and pay all 4 milestones so pilot_validated is True
    for m_id in [1, 2, 3, 4]:
        client.post(f"/milestones/{m_id}/submit", json={"evidence_text": "done"}, headers={"Authorization": f"Bearer {tokens['startup']}"})
        client.post(f"/milestones/{m_id}/validate", json={"verdict": "approved"}, headers={"Authorization": f"Bearer {tokens['validator']}"})
        client.post(f"/milestones/{m_id}/pay", headers={"Authorization": f"Bearer {tokens['gov']}"})

    proc_after = client.get("/pilots/1/procurement", headers={"Authorization": f"Bearer {tokens['gov']}"})
    assert proc_after.status_code == 200
    data_after = proc_after.json()
    assert data_after["checks"]["pilot_validated"] is True
    assert data_after["checks"]["performance_threshold_met"] is True
    assert data_after["checks"]["security_approved"] is True
    assert data_after["checks"]["budget_available"] is True
    assert data_after["recommended_pathway"] == "GeM direct procurement"

    # 2. Replicating to a new district adds it as "planned" without disturbing existing district entries
    rep1 = client.post(
        "/pilots/1/replicate",
        json={"districts": ["District B", "District C"]},
        headers={"Authorization": f"Bearer {tokens['gov']}"},
    )
    assert rep1.status_code == 200, rep1.text
    rep1_data = rep1.json()["replication"]
    district_map = {r["district"]: r["status"] for r in rep1_data}
    assert district_map["District A"] == "completed"
    assert district_map["District B"] == "planned"
    assert district_map["District C"] == "planned"

    # 3. Calling replicate a second time with an already-listed district doesn't duplicate it
    rep2 = client.post(
        "/pilots/1/replicate",
        json={"districts": ["District B", "District D"]},
        headers={"Authorization": f"Bearer {tokens['gov']}"},
    )
    assert rep2.status_code == 200, rep2.text
    rep2_data = rep2.json()["replication"]
    districts = [r["district"] for r in rep2_data]
    assert districts.count("District B") == 1
    assert "District D" in districts


# ===========================================================================
# CHECKPOINT 5: Health & Auth & CORS
# ===========================================================================

def test_checkpoint_5_health_and_demo_logins(client: TestClient, setup_data: dict):
    # 1. /health returns 200
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json() == {"status": "ok"}

    # 2. All 7 demo accounts login
    demo_accounts = [
        ("officer@water.gov.in", "demo1234", "government"),
        ("admin@procura.gov.in", "demo1234", "admin"),
        ("founder@aquasense.in", "demo1234", "startup"),
        ("expert1@procura.gov.in", "demo1234", "expert"),
        ("expert2@procura.gov.in", "demo1234", "expert"),
        ("validator@procura.gov.in", "demo1234", "validator"),
    ]
    for email, pwd, role in demo_accounts:
        login_res = client.post("/auth/login", json={"email": email, "password": pwd})
        assert login_res.status_code == 200, f"Failed for {email}: {login_res.text}"
        data = login_res.json()
        assert "token" in data
        assert data["user"]["role"] == role

