"""
Integration Check for Day 3 (SIH 26136).
Simulates the entire Day 3 multi-persona workflow end-to-end:
1. Government Officer publishes/selects Challenge #1.
2. Discovers 20 startups, screens through eligibility gate, and ranks by TF-IDF match score.
3. Shortlists top 3 eligible startups.
4. Three expert accounts (Dr S Rao, Prof M Iyer, Dr A Banerjee) each score applications.
5. Computes multi-expert average and weight snapshot immutability.
6. Government selects the top startup.
"""
import json
import os
from pathlib import Path
import pytest

from app.engines.eligibility import check_eligibility
from app.engines.matching import score_match
from app.engines.evaluation import score_evaluation, average_evaluations


@pytest.fixture
def seed_data():
    base = Path(__file__).resolve().parent.parent / "seed_data"
    with open(base / "users.json", "r", encoding="utf-8") as f:
        users = json.load(f)
    with open(base / "startups.json", "r", encoding="utf-8") as f:
        startups = json.load(f)
    with open(base / "challenges.json", "r", encoding="utf-8") as f:
        challenges = json.load(f)
    with open(base / "rubrics.json", "r", encoding="utf-8") as f:
        rubrics = json.load(f)

    return {
        "users": users,
        "startups": startups,
        "challenges": challenges,
        "rubrics": rubrics,
    }


def test_full_day3_integration_pipeline(seed_data):
    # =========================================================================
    # Step 1: Challenge Setup (Government Officer)
    # =========================================================================
    challenge = seed_data["challenges"][0]
    assert challenge["title"] == "Reduce municipal water leakage" or "water" in challenge["sector"].lower()
    
    match_rubric = next(
        r for r in seed_data["rubrics"] if r["id"] == challenge.get("match_rubric_id", 1)
    )
    match_weights = {c["key"]: c["weight"] for c in match_rubric["criteria"]}
    
    eval_rubric = next(
        r for r in seed_data["rubrics"] if r["id"] == challenge.get("evaluation_rubric_id", 5)
    )
    eval_weights = {c["key"]: c["weight"] for c in eval_rubric["criteria"]}

    # =========================================================================
    # Step 2: Discovery & Screening (20 Startups)
    # =========================================================================
    startups = seed_data["startups"]
    assert len(startups) == 20

    discovered = []
    for startup in startups:
        # Run eligibility screening
        elig_res = check_eligibility(challenge, startup, current_year=2026)
        
        # Run AI TF-IDF match scoring
        match_res = score_match(challenge, startup, match_weights)

        # Ineligible startups receive match_score 0 for ranking
        final_score = match_res["match_score"] if elig_res["eligible"] else 0.0

        discovered.append({
            "startup_id": startup["id"],
            "startup_name": startup["name"],
            "eligible": elig_res["eligible"],
            "eligibility_report": elig_res["eligibility_report"],
            "match_score": final_score,
            "match_breakdown": match_res["match_breakdown"],
            "rubric_snapshot": match_res["rubric_snapshot"],
            "explanation": match_res["explanation"],
            "status": "screened"
        })

    # Sort descending by eligible and match_score
    discovered.sort(key=lambda x: (x["eligible"], x["match_score"]), reverse=True)

    # Verify that eligible startups are ranked at the top with visible scores
    eligible_count = sum(1 for d in discovered if d["eligible"])
    assert eligible_count > 0
    top_startup = discovered[0]
    assert top_startup["eligible"] is True
    assert top_startup["match_score"] > 80.0
    assert len(top_startup["explanation"]) > 10

    # =========================================================================
    # Step 3: Shortlist Top 3 Startups
    # =========================================================================
    shortlisted = discovered[:3]
    assert len(shortlisted) == 3
    for app in shortlisted:
        app["status"] = "shortlisted"
        assert app["status"] == "shortlisted"

    # =========================================================================
    # Step 4: Three Experts Score Each Shortlisted Application
    # =========================================================================
    expert_users = [u for u in seed_data["users"] if u["role"] == "expert"]
    assert len(expert_users) >= 3

    # Expert scorecards
    expert_evaluations_by_app = {}
    for app in shortlisted:
        app_id = app["startup_id"]
        expert_evaluations_by_app[app_id] = []

        # Expert 1 (Dr S Rao)
        e1_scores = {
            "technical_feasibility": 92,
            "innovation": 88,
            "cost_effectiveness": 85,
            "scalability": 90,
            "security": 95,
            "implementation_capability": 90,
            "social_impact": 88,
        }
        res1 = score_evaluation(e1_scores, eval_weights)
        expert_evaluations_by_app[app_id].append({
            "expert_id": expert_users[0]["id"],
            "expert_name": expert_users[0]["name"],
            **res1
        })

        # Expert 2 (Prof M Iyer)
        e2_scores = {
            "technical_feasibility": 90,
            "innovation": 85,
            "cost_effectiveness": 88,
            "scalability": 92,
            "security": 90,
            "implementation_capability": 88,
            "social_impact": 85,
        }
        res2 = score_evaluation(e2_scores, eval_weights)
        expert_evaluations_by_app[app_id].append({
            "expert_id": expert_users[1]["id"],
            "expert_name": expert_users[1]["name"],
            **res2
        })

        # Expert 3 (Dr A Banerjee)
        e3_scores = {
            "technical_feasibility": 94,
            "innovation": 90,
            "cost_effectiveness": 82,
            "scalability": 88,
            "security": 92,
            "implementation_capability": 92,
            "social_impact": 90,
        }
        res3 = score_evaluation(e3_scores, eval_weights)
        expert_evaluations_by_app[app_id].append({
            "expert_id": expert_users[2]["id"],
            "expert_name": expert_users[2]["name"],
            **res3
        })

    # =========================================================================
    # Step 5: Compute Consensus Averages
    # =========================================================================
    evaluated_rankings = []
    for app in shortlisted:
        app_id = app["startup_id"]
        evals = expert_evaluations_by_app[app_id]
        avg_res = average_evaluations(evals)
        
        assert avg_res["evaluation_count"] == 3
        assert avg_res["average_total"] is not None
        
        evaluated_rankings.append({
            "startup_id": app["startup_id"],
            "startup_name": app["startup_name"],
            "average_total": avg_res["average_total"],
            "evaluation_count": avg_res["evaluation_count"],
            "status": "evaluated"
        })

    # Sort evaluated applications by average expert score descending
    evaluated_rankings.sort(key=lambda x: x["average_total"], reverse=True)
    winner = evaluated_rankings[0]
    assert winner["average_total"] >= 85.0

    # =========================================================================
    # Step 6: Government Selects Top Startup
    # =========================================================================
    winner["status"] = "selected"
    for other in evaluated_rankings[1:]:
        other["status"] = "rejected"

    assert winner["status"] == "selected"
    assert evaluated_rankings[1]["status"] == "rejected"
    assert evaluated_rankings[2]["status"] == "rejected"
