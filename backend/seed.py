"""
Seeds the database from the real files in seed_data/. Run from backend/:

    python seed.py

Idempotent: safe to run multiple times, existing rows are left alone.
"""
import json
from datetime import date, datetime

from sqlmodel import Session, select

from app.auth import hash_password
from app.db import engine, create_db_and_tables
from app.models import Challenge, Rubric, Startup, User


def seed():
    create_db_and_tables()

    with Session(engine) as session:

        # -------------------------
        # USERS — the 7 documented demo accounts, from docs/API.md section 13
        # -------------------------
        with open("seed_data/users.json") as f:
            user_data = json.load(f)

        for data in user_data:
            if session.get(User, data["id"]) is not None:
                continue
            session.add(User(
                id=data["id"],
                name=data["name"],
                email=data["email"],
                password_hash=hash_password(data["password"]),
                role=data["role"],
                department=data.get("department"),
                district=data.get("district"),
            ))
        session.commit()

        # -------------------------
        # RUBRICS — 4 match + 2 evaluation, from seed_data/rubrics.json
        # -------------------------
        with open("seed_data/rubrics.json") as f:
            rubric_data = json.load(f)

        # admin user (id 2, "Platform Admin") owns the seeded rubrics
        admin_id = next((u["id"] for u in user_data if u["role"] == "admin"), 1)

        for r in rubric_data:
            if session.get(Rubric, r["id"]) is not None:
                continue
            weights = {c["key"]: c["weight"] for c in r["criteria"]}
            session.add(Rubric(
                id=r["id"],
                name=r["name"],
                kind=r["kind"],
                weights_json=weights,
                criteria_json=r["criteria"],
                version=r["version"],
                is_default=r["is_default"],
                active=r["active"],
                created_by=admin_id,
                created_at=datetime.utcnow(),
            ))
        session.commit()

        # -------------------------
        # STARTUPS — 20 across 4 sectors, from seed_data/startups.json
        # -------------------------
        with open("seed_data/startups.json") as f:
            startup_data = json.load(f)

        for data in startup_data:
            if session.get(Startup, data["id"]) is not None:
                continue
            session.add(Startup(
                id=data["id"],
                user_id=data["user_id"],
                name=data["name"],
                sector=data["sector"],
                technologies=data.get("technologies", []),
                tech_tags=data.get("tech_tags", []),
                dpiit_number=data.get("dpiit_number"),
                incorporation_year=data.get("incorporation_year"),
                turnover=data.get("turnover"),
                team_size=data.get("team_size"),
                past_projects=data.get("past_projects", []),
                certifications=data.get("certifications", []),
                description=data.get("description"),
            ))
        session.commit()

        # -------------------------
        # CHALLENGES — 3 seeded challenges, from seed_data/challenges.json
        # Field names in the file already match the Challenge model 1:1.
        # -------------------------
        with open("seed_data/challenges.json") as f:
            challenge_data = json.load(f)

        for c in challenge_data:
            if session.get(Challenge, c["id"]) is not None:
                continue
            c = dict(c)
            c["deadline"] = date.fromisoformat(c["deadline"])  # JSON gives a string, model needs a date
            session.add(Challenge(**c))
        session.commit()

        print(f"Seeded {len(user_data)} users, {len(rubric_data)} rubrics, "
              f"{len(startup_data)} startups, {len(challenge_data)} challenges.")


if __name__ == "__main__":
    seed()
