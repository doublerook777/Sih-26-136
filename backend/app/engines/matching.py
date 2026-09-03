"""
Startup-to-Challenge Matching Engine for ProcuraAI (SIH 26136).
Pure function executing 6-factor weighted scoring.
Zero database imports, zero network calls.
"""
from typing import Any, Dict, List, Optional, Set
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Adjacency matrix for public sector domains
# exact = 100, adjacent = 60, unrelated = 20
SECTOR_ADJACENCIES: Dict[str, Set[str]] = {
    "water": {"waste"},
    "waste": {"water", "transport"},
    "transport": {"waste"},
    "healthcare": set(),
}

# Standard 12-tag technology vocabulary across challenges and startups
TECH_VOCABULARY = [
    "iot",
    "sensors",
    "ai",
    "computer-vision",
    "analytics",
    "cloud",
    "mobile-app",
    "gis",
    "telematics",
    "robotics",
    "edge-computing",
    "automation",
]


def _compute_technology_match(required_tech: List[str], tech_tags: List[str]) -> float:
    """
    Computes TF-IDF cosine similarity between challenge's required_tech and startup's tech_tags.
    Both are drawn from the standardized 12-tag vocabulary. Never scores against free-text technologies.
    Returns a score between 0.0 and 100.0.
    """
    clean_req = [str(t).strip().lower() for t in required_tech if t]
    clean_tags = [str(t).strip().lower() for t in tech_tags if t]

    if not clean_req:
        return 100.0 if clean_tags else 0.0
    if not clean_tags:
        return 0.0

    doc_req = " ".join(clean_req)
    doc_tags = " ".join(clean_tags)

    # If sets are identical, return exact 100.0
    if set(clean_req) == set(clean_tags):
        return 100.0

    # TF-IDF cosine similarity with token pattern supporting hyphens
    try:
        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b[\w-]+\b")
        tfidf_matrix = vectorizer.fit_transform([doc_req, doc_tags])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(max(0.0, min(sim * 100.0, 100.0)))
    except Exception:
        # Fallback to Jaccard-based overlap if vectorization fails
        overlap = len(set(clean_req).intersection(set(clean_tags)))
        return float((overlap / len(clean_req)) * 100.0)


def _compute_domain_experience(challenge_sector: str, startup_sector: str) -> float:
    """
    Scores sector relevance:
    - Exact match: 100.0
    - Adjacent domain: 60.0 (e.g. water <-> waste, waste <-> transport)
    - Unrelated domain: 20.0
    """
    c_sec = (challenge_sector or "").strip().lower()
    s_sec = (startup_sector or "").strip().lower()

    if not c_sec or not s_sec:
        return 20.0
    if c_sec == s_sec:
        return 100.0
    if s_sec in SECTOR_ADJACENCIES.get(c_sec, set()):
        return 60.0
    return 20.0


def _compute_past_projects(challenge_sector: str, past_projects: List[Dict[str, Any]]) -> float:
    """
    Counts startup past projects whose sector matches the challenge sector.
    Normalized against 3 projects as a reasonable ceiling, capped at 100.0.
    """
    c_sec = (challenge_sector or "").strip().lower()
    if not past_projects or not c_sec:
        return 0.0

    relevant_count = sum(
        1 for p in past_projects
        if str(p.get("sector", "")).strip().lower() == c_sec
    )
    return float(min(relevant_count / 3.0, 1.0) * 100.0)


def _compute_cost_fit(
    budget: Optional[int],
    quote: Optional[int],
) -> tuple[float, bool]:
    """
    Calculates cost fit score: (1 - abs(quote - budget) / budget) * 100.0, clamped [0, 100].
    If no quote is provided, returns neutral score 75.0 and flag indicating neutral quote.
    """
    if quote is None or budget is None or budget <= 0:
        return 75.0, True

    diff = abs(quote - budget) / float(budget)
    score = (1.0 - diff) * 100.0
    return float(max(0.0, min(score, 100.0))), False


def _compute_scalability(team_size: Optional[int], past_projects: List[Dict[str, Any]]) -> float:
    """
    Calculates scalability from team capacity and deployment history:
    - Team size component (0 - 50 pts): min(team_size / 20.0, 1.0) * 50.0
    - Prior deployments component (0 - 50 pts): min(len(past_projects) / 3.0, 1.0) * 50.0
    Total score is the sum, capped at 100.0.
    """
    t_size = team_size or 0
    deploy_count = len(past_projects or [])

    team_score = min(t_size / 20.0, 1.0) * 50.0
    deploy_score = min(deploy_count / 3.0, 1.0) * 50.0
    return float(min(team_score + deploy_score, 100.0))


def _generate_explanation(
    startup_name: str,
    challenge_sector: str,
    matched_tech_count: int,
    total_req_tech: int,
    relevant_projects_count: int,
    quote: Optional[int],
    budget: Optional[int],
    is_neutral_quote: bool,
    is_eligible: bool,
) -> str:
    """
    Generates a concise, evidence-based natural language explanation naming real factors.
    """
    reasons = []

    # Tech overlap
    if total_req_tech > 0:
        reasons.append(f"capabilities matching {matched_tech_count} of {total_req_tech} required technologies")
    else:
        reasons.append("aligned technology capabilities")

    # Sector projects
    sec_display = challenge_sector.replace("_", " ").lower()
    if relevant_projects_count >= 1:
        s = "s" if relevant_projects_count > 1 else ""
        reasons.append(f"{relevant_projects_count} prior {sec_display}-sector deployment{s}")
    else:
        reasons.append(f"exposure in the {sec_display} domain")

    # Quote/budget
    if not is_neutral_quote and quote is not None and budget is not None and budget > 0:
        if quote <= budget:
            under_pct = round(((budget - quote) / budget) * 100)
            if under_pct > 0:
                reasons.append(f"a quote {under_pct}% under budget")
            else:
                reasons.append("a quote exactly matching the budget ceiling")
        else:
            over_pct = round(((quote - budget) / budget) * 100)
            reasons.append(f"a quote {over_pct}% above the budget ceiling")
    else:
        reasons.append("a neutral cost fit assigned (quote not submitted)")

    prefix = "Recommended because the startup has " if is_eligible else "Screened match (ineligible gates flagged): startup has "
    return prefix + ", ".join(reasons) + "."


def score_match(
    challenge: Dict[str, Any],
    startup: Dict[str, Any],
    weights: Dict[str, float | int],
    eligibility: Optional[Dict[str, Any] | bool] = None,
    quote: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Calculates the 6-factor weighted match score between a challenge and startup.
    Weights are supplied dynamically by the caller (from the challenge's rubric).

    Returns:
        {
            "match_score": float (0.0 to 100.0, 1 decimal place),
            "match_breakdown": {
                "technology_match": float (0-100),
                "domain_experience": float (0-100),
                "past_projects": float (0-100),
                "eligibility": float (0 or 100),
                "cost_fit": float (0-100),
                "scalability": float (0-100),
            },
            "rubric_snapshot": dict (copy of input weights),
            "explanation": str (dynamic rationale naming real factors),
        }
    """
    req_tech = challenge.get("required_tech", [])
    tech_tags = startup.get("tech_tags", [])
    c_sector = challenge.get("sector", "")
    s_sector = startup.get("sector", "")
    past_projects = startup.get("past_projects", [])
    team_size = startup.get("team_size")
    budget = challenge.get("budget")
    effective_quote = quote if quote is not None else startup.get("quote")

    # 1. Technology match (TF-IDF Cosine Similarity)
    tech_score = _compute_technology_match(req_tech, tech_tags)

    # 2. Domain experience (exact=100, adjacent=60, unrelated=20)
    domain_score = _compute_domain_experience(c_sector, s_sector)

    # 3. Past projects (in-sector count normalized to 3)
    projects_score = _compute_past_projects(c_sector, past_projects)

    # 4. Eligibility gate score (100 if passed, 0 if failed)
    if isinstance(eligibility, dict):
        is_eligible = bool(eligibility.get("eligible", False))
    elif isinstance(eligibility, bool):
        is_eligible = eligibility
    else:
        is_eligible = bool(startup.get("eligible", True))
    eligibility_score = 100.0 if is_eligible else 0.0

    # 5. Cost fit (clamped percentage deviation or neutral 75)
    cost_score, is_neutral_quote = _compute_cost_fit(budget, effective_quote)

    # 6. Scalability (team size + prior deployments)
    scalability_score = _compute_scalability(team_size, past_projects)

    breakdown = {
        "technology_match": round(tech_score, 1),
        "domain_experience": round(domain_score, 1),
        "past_projects": round(projects_score, 1),
        "eligibility": round(eligibility_score, 1),
        "cost_fit": round(cost_score, 1),
        "scalability": round(scalability_score, 1),
    }

    # Calculate weighted total using weights supplied by the caller
    total_weighted = sum(
        (breakdown[key] * float(weights.get(key, 0))) / 100.0
        for key in breakdown
    )
    match_score = round(total_weighted, 1)

    # Extract matched count for explanation
    clean_req = [str(t).strip().lower() for t in req_tech if t]
    clean_tags = [str(t).strip().lower() for t in tech_tags if t]
    matched_count = len(set(clean_req).intersection(set(clean_tags)))
    rel_projects_count = sum(
        1 for p in past_projects
        if str(p.get("sector", "")).strip().lower() == str(c_sector).strip().lower()
    )

    explanation = _generate_explanation(
        startup_name=startup.get("name", "Startup"),
        challenge_sector=c_sector,
        matched_tech_count=matched_count,
        total_req_tech=len(clean_req),
        relevant_projects_count=rel_projects_count,
        quote=effective_quote,
        budget=budget,
        is_neutral_quote=is_neutral_quote,
        is_eligible=is_eligible,
    )

    return {
        "match_score": match_score,
        "match_breakdown": breakdown,
        "rubric_snapshot": dict(weights),  # explicit copy
        "explanation": explanation,
    }
