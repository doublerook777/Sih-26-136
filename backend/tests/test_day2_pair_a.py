import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.db import get_session
from app.auth import create_access_token, hash_password
from app.models import User, Startup, Challenge, Application, Pilot, Milestone


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Seed test users
        gov_user = User(
            id=1,
            name="Gov Officer",
            email="gov@test.com",
            password_hash=hash_password("password123"),
            role="government",
            department="Water Resources",
            district="District A",
        )
        startup_user = User(
            id=2,
            name="Startup Founder",
            email="startup@test.com",
            password_hash=hash_password("password123"),
            role="startup",
        )
        expert_user = User(
            id=3,
            name="Dr Expert",
            email="expert@test.com",
            password_hash=hash_password("password123"),
            role="expert",
        )
        session.add(gov_user)
        session.add(startup_user)
        session.add(expert_user)
        session.commit()

        # Seed test startup linked to startup_user
        startup = Startup(
            id=1,
            user_id=startup_user.id,
            name="AquaSense Innovations",
            sector="water",
            technologies=["IoT", "Sensors", "AI"],
            dpiit_number="DIPP12345",
            incorporation_year=2022,
            team_size=8,
            turnover=5000000,
            certifications=["ISO 27001"],
            description="Real-time acoustic leak detection.",
            past_projects=[{"name": "City pipeline audit", "sector": "water", "year": 2024}],
        )
        session.add(startup)
        session.commit()

        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="gov_token")
def gov_token_fixture():
    return create_access_token(1)


@pytest.fixture(name="startup_token")
def startup_token_fixture():
    return create_access_token(2)


@pytest.fixture(name="expert_token")
def expert_token_fixture():
    return create_access_token(3)


# -----------------------------------------------------------------------------
# 1. AI Generate Statement Tests
# -----------------------------------------------------------------------------
def test_ai_generate_statement_success(client: TestClient, gov_token: str):
    response = client.post(
        "/ai/generate-statement",
        headers={"Authorization": f"Bearer {gov_token}"},
        json={
            "title": "Leakage Detection",
            "raw_description": "Our municipal pipes leak continuously.",
            "department": "Water Resources",
            "district": "District A",
            "sector": "water",
            "budget": 1000000,
            "timeline_days": 90,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "problem" in data
    assert "background" in data
    assert "existing_system" in data
    assert "identified_gap" in data
    assert "desired_solution" in data
    assert "target_users" in data
    assert "technical_requirements" in data
    assert "constraints" in data
    assert "budget" in data
    assert "timeline" in data
    assert "expected_outcomes" in data
    assert "kpis" in data
    assert "eligibility_requirements" in data
    assert "data_requirements" in data
    assert "security_requirements" in data
    assert data["generated_by"] in ["llm", "template"]


def test_ai_generate_statement_unauthorized_role(client: TestClient, startup_token: str):
    response = client.post(
        "/ai/generate-statement",
        headers={"Authorization": f"Bearer {startup_token}"},
        json={"raw_description": "Test raw problem"},
    )
    assert response.status_code == 403


# -----------------------------------------------------------------------------
# 2. Challenge Creation & Retrieval (Day 2 Deliverables)
# -----------------------------------------------------------------------------
def test_create_challenge_persists_statement(client: TestClient, gov_token: str):
    payload = {
        "title": "Reduce municipal water leakage",
        "raw_description": "Our pipes leak and we only find out when a road floods.",
        "department": "Urban Water Supply",
        "district": "District A",
        "sector": "water",
        "budget": 1000000,
        "timeline_days": 90,
        "deadline": "2026-09-15",
        "required_tech": ["iot", "sensors", "analytics"],
        "match_rubric_id": 1,
        "evaluation_rubric_id": 5,
        "eligibility_rules": {
            "registered_startup": True,
            "required_certification": "ISO 27001",
            "min_experience_years": 2,
            "min_technology_overlap": 1,
            "max_quote": 1000000,
            "security_baseline": True,
        },
        "kpi_targets": [
            {
                "name": "Water wastage",
                "unit": "%",
                "baseline": 30,
                "target": 20,
                "category": "impact",
                "direction": "lower_is_better",
            }
        ],
    }

    response = client.post(
        "/challenges",
        headers={"Authorization": f"Bearer {gov_token}"},
        json=payload,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Reduce municipal water leakage"
    assert data["sector"] == "water"
    assert data["status"] == "draft"
    assert "statement" in data
    assert len(data["statement"]) >= 15
    assert data["eligibility_rules"]["registered_startup"] is True
    assert len(data["kpi_targets"]) == 1
    assert data["application_count"] == 0


def test_get_challenge_by_id(client: TestClient, gov_token: str):
    # First create
    create_res = client.post(
        "/challenges",
        headers={"Authorization": f"Bearer {gov_token}"},
        json={
            "title": "Waste Sorting Challenge",
            "raw_description": "Sort recyclable municipal waste automatically.",
            "department": "Urban Sanitation",
            "district": "District B",
            "sector": "waste",
            "budget": 500000,
            "timeline_days": 60,
        },
    )
    challenge_id = create_res.json()["id"]

    # Now get
    get_res = client.get(
        f"/challenges/{challenge_id}",
        headers={"Authorization": f"Bearer {gov_token}"},
    )
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == challenge_id
    assert data["title"] == "Waste Sorting Challenge"
    assert "statement" in data
    assert data["application_count"] == 0


def test_get_challenges_list_with_filtering(client: TestClient, gov_token: str):
    # Create two challenges
    client.post(
        "/challenges",
        headers={"Authorization": f"Bearer {gov_token}"},
        json={
            "title": "Water Pilot",
            "raw_description": "Water desc",
            "department": "Water",
            "district": "District A",
            "sector": "water",
            "status": "open",
        },
    )
    client.post(
        "/challenges",
        headers={"Authorization": f"Bearer {gov_token}"},
        json={
            "title": "Health Pilot",
            "raw_description": "Health desc",
            "department": "Health",
            "district": "District A",
            "sector": "healthcare",
            "status": "draft",
        },
    )

    # Filter sector=water
    res_water = client.get("/challenges?sector=water")
    assert res_water.status_code == 200
    items = res_water.json()
    assert len(items) >= 1
    assert all(i["sector"] == "water" for i in items)


# -----------------------------------------------------------------------------
# 3. Application Submission & Retrieval (Day 2 Deliverables)
# -----------------------------------------------------------------------------
def test_startup_apply_to_challenge(
    client: TestClient, gov_token: str, startup_token: str
):
    # 1. Create a challenge
    ch_res = client.post(
        "/challenges",
        headers={"Authorization": f"Bearer {gov_token}"},
        json={
            "title": "Water Leak Detection",
            "raw_description": "Detect pipeline leaks",
            "department": "Water Supply",
            "district": "District A",
            "sector": "water",
            "required_tech": ["IoT", "Sensors"],
            "budget": 1000000,
            "timeline_days": 90,
        },
    )
    challenge_id = ch_res.json()["id"]

    # 2. Startup applies
    app_res = client.post(
        "/applications",
        headers={"Authorization": f"Bearer {startup_token}"},
        json={
            "challenge_id": challenge_id,
            "quote": 850000,
            "pitch": "We propose acoustic sensors at 40 nodes.",
        },
    )
    assert app_res.status_code == 201
    data = app_res.json()
    assert data["application_id"] is not None
    assert data["startup_id"] == 1
    assert data["startup_name"] == "AquaSense Innovations"
    assert "eligible" in data
    assert "match_score" in data
    assert "rubric_snapshot" in data
    assert data["status"] == "applied"

    # 3. Verify application appears in GET /challenges/{id}/applications
    list_res = client.get(
        f"/challenges/{challenge_id}/applications",
        headers={"Authorization": f"Bearer {gov_token}"},
    )
    assert list_res.status_code == 200
    apps = list_res.json()
    assert len(apps) == 1
    assert apps[0]["application_id"] == data["application_id"]
    assert apps[0]["startup_name"] == "AquaSense Innovations"


def test_startup_apply_role_protection(client: TestClient, gov_token: str):
    # Gov user trying to apply as a startup should receive 403
    app_res = client.post(
        "/applications",
        headers={"Authorization": f"Bearer {gov_token}"},
        json={"challenge_id": 1, "quote": 500000},
    )
    assert app_res.status_code == 403


# -----------------------------------------------------------------------------
# 4. Documents Router & Jinja2 Templates (Day 2 Deliverables)
# -----------------------------------------------------------------------------
def test_documents_templates_catalog(client: TestClient, gov_token: str):
    res = client.get(
        "/documents/templates",
        headers={"Authorization": f"Bearer {gov_token}"},
    )
    assert res.status_code == 200
    templates = res.json()
    assert len(templates) == 13
    doc_types = [t["doc_type"] for t in templates]
    assert "problem_statement" in doc_types
    assert "eligibility_criteria" in doc_types
    assert "evaluation_criteria" in doc_types
    assert "pilot_agreement" in doc_types
    assert "milestone_contract" in doc_types


def test_documents_render_problem_statement(
    client: TestClient, gov_token: str
):
    # Create challenge
    ch_res = client.post(
        "/challenges",
        headers={"Authorization": f"Bearer {gov_token}"},
        json={
            "title": "Smart Metering System",
            "raw_description": "Smart automated water meter reading across city wards.",
            "department": "Municipal Admin",
            "district": "Bengaluru",
            "sector": "water",
            "budget": 2500000,
            "timeline_days": 120,
        },
    )
    challenge_id = ch_res.json()["id"]

    # Request rendered HTML
    doc_res = client.get(
        f"/documents/problem_statement/{challenge_id}",
        headers={"Authorization": f"Bearer {gov_token}"},
    )
    assert doc_res.status_code == 200
    assert "text/html" in doc_res.headers.get("content-type", "")
    html_text = doc_res.text
    assert "Smart Metering System" in html_text
    assert "Problem Description" in html_text
    assert "ProcuraAI" in html_text
    assert "Section 01" in html_text


def test_documents_render_eligibility_criteria(
    client: TestClient, gov_token: str
):
    ch_res = client.post(
        "/challenges",
        headers={"Authorization": f"Bearer {gov_token}"},
        json={
            "title": "Air Quality Tracking",
            "raw_description": "Hyperlocal AQI sensor grid.",
            "department": "Pollution Control Board",
            "district": "Delhi NCR",
            "sector": "environment",
        },
    )
    challenge_id = ch_res.json()["id"]

    doc_res = client.get(
        f"/documents/eligibility_criteria/{challenge_id}",
        headers={"Authorization": f"Bearer {gov_token}"},
    )
    assert doc_res.status_code == 200
    assert "text/html" in doc_res.headers.get("content-type", "")
    assert "Air Quality Tracking" in doc_res.text
    assert "Mandatory Eligibility Framework" in doc_res.text


def test_documents_render_pilot_agreement(
    client: TestClient, session: Session, gov_token: str
):
    # Create a pilot record in DB
    pilot = Pilot(
        id=1,
        challenge_id=1,
        startup_id=1,
        location="Ward 42, North District",
        duration_days=90,
        budget=1000000,
        objectives="Deploy 50 IoT acoustic sensors.",
        security_status="passed",
        risk_level="low",
        status="active",
    )
    session.add(pilot)
    session.commit()

    doc_res = client.get(
        "/documents/pilot_agreement/1",
        headers={"Authorization": f"Bearer {gov_token}"},
    )
    assert doc_res.status_code == 200
    assert "text/html" in doc_res.headers.get("content-type", "")
    assert "Master Pilot Agreement" in doc_res.text
    assert "16-Clause Master Agreement" in doc_res.text


def test_documents_unknown_type_404(client: TestClient, gov_token: str):
    doc_res = client.get(
        "/documents/non_existent_doc_type/1",
        headers={"Authorization": f"Bearer {gov_token}"},
    )
    assert doc_res.status_code == 404
