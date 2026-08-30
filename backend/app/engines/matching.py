def check_eligibility(startup, challenge):
    rules = challenge.eligibility_rules_json or {}

    report = {
        "dpiit_registered": True,
        "minimum_team_size": True,
        "reasons": []
    }

    if rules.get("dpiit_registered"):
        if not startup.dpiit_number:
            report["dpiit_registered"] = False
            report["reasons"].append("Startup is not DPIIT registered.")

    if rules.get("minimum_team_size"):
        minimum = rules["minimum_team_size"]
        if (startup.team_size or 0) < minimum:
            report["minimum_team_size"] = False
            report["reasons"].append(
                f"Team size must be at least {minimum}."
            )

    eligible = all(
        value is True
        for key, value in report.items()
        if key != "reasons"
    )

    return {
        "eligible": eligible,
        "eligibility_report": report,
        "report": report
    }
MATCH_WEIGHTS = {
    "technology_match": 30,
    "domain_experience": 20,
    "past_projects": 15,
    "eligibility": 15,
    "cost_fit": 10,
    "scalability": 10,
}


def calculate_match_score(startup, challenge, eligible):
    required_tech = {
        tech.lower()
        for tech in (challenge.required_tech or [])
    }

    startup_tech = {
        tech.lower()
        for tech in (startup.technologies or [])
    }

    if required_tech:
        technology_match = (
            len(required_tech & startup_tech)
            / len(required_tech)
        ) * 100
    else:
        technology_match = 100.0

    domain_experience = (
        100.0
        if startup.sector.lower() == challenge.sector.lower()
        else 40.0
    )

    projects = startup.past_projects or []

    matching_projects = [
        project
        for project in projects
        if project.get("sector", "").lower()
        == challenge.sector.lower()
    ]

    past_projects = min(
        100.0,
        len(matching_projects) * 35.0
    )

    eligibility = 100.0 if eligible else 0.0

    cost_fit = 80.0 if startup.turnover else 40.0

    team_size = startup.team_size or 0

    if team_size >= 20:
        scalability = 100.0
    elif team_size >= 10:
        scalability = 85.0
    elif team_size >= 5:
        scalability = 70.0
    else:
        scalability = 50.0

    breakdown = {
        "technology_match": round(technology_match, 2),
        "domain_experience": round(domain_experience, 2),
        "past_projects": round(past_projects, 2),
        "eligibility": round(eligibility, 2),
        "cost_fit": round(cost_fit, 2),
        "scalability": round(scalability, 2),
    }

    score = sum(
        breakdown[key] * MATCH_WEIGHTS[key] / 100
        for key in MATCH_WEIGHTS
    )

    return round(score, 2), breakdown


def match_startup(startup, challenge):
    eligibility_result = check_eligibility(
        startup,
        challenge
    )

    eligible = eligibility_result["eligible"]

    if not eligible:
        score = 0.0
        breakdown = {
            key: 0.0
            for key in MATCH_WEIGHTS
        }
    else:
        score, breakdown = calculate_match_score(
            startup,
            challenge,
            eligible
        )

    return {
        "eligible": eligible,
        "eligibility_report": eligibility_result[
            "eligibility_report"
        ],
        "match_score": score,
        "match_breakdown": breakdown,
        "rubric_snapshot": MATCH_WEIGHTS.copy(),
        "explanation": (
            f"Recommended because {startup.name} matches "
            f"the challenge requirements."
            if eligible
            else "Not eligible because one or more "
                 "eligibility checks failed."
        ),
    }
