import json
from datetime import date

from sqlmodel import Session

from app.auth import hash_password
from app.db import engine, create_db_and_tables
from app.models import User, Startup, Challenge


def seed():
    create_db_and_tables()

    with Session(engine) as session:

        # -------------------------
        # USERS
        # -------------------------
        users = [
            User(
                id=1,
                name="Admin User",
                email="admin@procura.com",
                password_hash=hash_password("admin123"),
                role="admin",
            ),
            User(
                id=2,
                name="Startup User",
                email="startup@procura.com",
                password_hash=hash_password("startup123"),
                role="startup",
            ),
            User(
                id=3,
                name="Government User",
                email="gov@procura.com",
                password_hash=hash_password("gov123"),
                role="government",
            ),
            User(
                id=4,
                name="R Kumar",
                email="officer@water.gov.in",
                password_hash=hash_password("demo1234"),
                role="government",
            ),
            User(
                id=5,
                name="Platform Admin",
                email="admin@procura.gov.in",
                password_hash=hash_password("demo1234"),
                role="admin",
            ),
            User(
                id=6,
                name="AquaSense",
                email="founder@aquasense.in",
                password_hash=hash_password("demo1234"),
                role="startup",
            ),
            User(
                id=7,
                name="Dr S Rao",
                email="expert1@procura.gov.in",
                password_hash=hash_password("demo1234"),
                role="expert",
            ),
            User(
                id=8,
                name="Prof M Iyer",
                email="expert2@procura.gov.in",
                password_hash=hash_password("demo1234"),
                role="expert",
            ),
            User(
                id=9,
                name="Dr A Banerjee",
                email="expert3@procura.gov.in",
                password_hash=hash_password("demo1234"),
                role="expert",
            ),
            User(
                id=10,
                name="N Sharma",
                email="validator@procura.gov.in",
                password_hash=hash_password("demo1234"),
                role="validator",
            ),
        ]

        for user in users:
            if session.get(User, user.id) is None:
                session.add(user)

        session.commit()

        # -------------------------
        # STARTUPS
        # -------------------------
        with open("seed_data/startups.json", "r") as f:
            startup_data = json.load(f)

        for data in startup_data:
            if session.get(Startup, data["id"]) is not None:
                continue

            startup = Startup(
                id=data["id"],
                user_id=data["user_id"],
                name=data["name"],
                sector=data["sector"],
                technologies=data.get("technologies", []),
                dpiit_number=data.get("dpiit_number"),
                incorporation_year=data.get("incorporation_year"),
                turnover=data.get("turnover"),
                team_size=data.get("team_size"),
                past_projects=data.get("past_projects", []),
                certifications=data.get("certifications", []),
                description=data.get("description"),
            )

            session.add(startup)

        session.commit()

        # -------------------------
        # CHALLENGES
        # -------------------------
        challenges = [
            Challenge(
                created_by=3,
                department="Water Resources",
                district="Bengaluru Urban",
                title="Smart Water Leakage Detection",
                raw_description="Detect and reduce water pipeline leakage using sensors and AI.",
                statement_json={
                    "problem": "Water loss due to undetected pipeline leakage.",
                    "expected_solution": "Sensor-based monitoring with AI anomaly detection.",
                },
                sector="water",
                required_tech=["IoT", "Sensors", "AI", "Analytics"],
                eligibility_rules_json={
                    "minimum_team_size": 2,
                    "dpiit_registered": True,
                },
                kpi_targets_json={
                    "leakage_reduction_percent": 20,
                    "detection_time_hours": 24,
                },
                budget=5000000,
                timeline_days=180,
                deadline=date(2026, 12, 31),
                status="open",
            ),
            Challenge(
                created_by=3,
                department="Urban Development",
                district="Bengaluru Urban",
                title="AI-Based Traffic Management",
                raw_description="Improve traffic flow using real-time data and AI-based prediction.",
                statement_json={
                    "problem": "Traffic congestion causes delays and increased emissions.",
                    "expected_solution": "AI-powered traffic monitoring and prediction.",
                },
                sector="smart_city",
                required_tech=["AI", "Machine Learning", "IoT", "Analytics"],
                eligibility_rules_json={
                    "minimum_team_size": 2,
                    "dpiit_registered": True,
                },
                kpi_targets_json={
                    "travel_time_reduction_percent": 15,
                    "congestion_reduction_percent": 20,
                },
                budget=7500000,
                timeline_days=180,
                deadline=date(2026, 12, 31),
                status="open",
            ),
            Challenge(
                created_by=3,
                department="Environment",
                district="Bengaluru Urban",
                title="Smart Waste Management",
                raw_description="Improve municipal waste collection and monitoring using technology.",
                statement_json={
                    "problem": "Inefficient waste collection and limited monitoring.",
                    "expected_solution": "IoT-enabled collection monitoring and route optimization.",
                },
                sector="waste_management",
                required_tech=["IoT", "GPS", "AI", "Analytics"],
                eligibility_rules_json={
                    "minimum_team_size": 2,
                    "dpiit_registered": True,
                },
                kpi_targets_json={
                    "collection_efficiency_percent": 25,
                    "fuel_reduction_percent": 15,
                },
                budget=4000000,
                timeline_days=150,
                deadline=date(2026, 12, 31),
                status="open",
            ),
        ]

        existing_challenges = session.exec(
            Challenge.__table__.select()
        ).all()

        if not existing_challenges:
            session.add_all(challenges)
            session.commit()

        print(f"Seeded {len(startup_data)} startups.")
        print("Users checked/created.")
        print("3 challenges checked/created.")


if __name__ == "__main__":
    seed()