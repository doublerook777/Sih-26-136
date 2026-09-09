"""
Sector / required-tech suggestion for ProcuraAI (SIH 26136).

Deterministic keyword classifier that reads an officer's raw problem description
and suggests a sector (one of the platform's 4 fixed sectors) and a shortlist of
required-tech tags (drawn only from the matching engine's fixed 12-tag vocabulary).

This exists so the AI-generation step can nudge the Create Challenge form's Sector
and Required Technologies fields toward the actual problem being described, instead
of silently leaving them on their previous values while only the prose changes.

Pure function: no DB imports, no network calls, always returns a result.
"""
import re
from typing import Any, Dict, List, Optional

from app.engines.matching import TECH_VOCABULARY


def _contains_keyword(text: str, keyword: str) -> bool:
    """Word-boundary match so short keywords (e.g. 'ai') don't fire inside unrelated
    words (e.g. 'domain', 'maintain', 'again')."""
    pattern = r"\b" + re.escape(keyword.strip()) + r"\b"
    return re.search(pattern, text) is not None


# Keyword hints per sector. Every entry is matched as a whole word/phrase.
SECTOR_KEYWORDS: Dict[str, List[str]] = {
    "water": [
        "water", "pipe", "pipes", "pipeline", "leak", "leakage", "sewage",
        "drainage", "reservoir", "potable", "non-revenue water", "nrw", "tap",
        "borewell", "stormwater",
    ],
    "healthcare": [
        "hospital", "hospitals", "patient", "patients", "health", "opd",
        "triage", "clinic", "medical", "doctor", "nurse", "diagnosis",
        "ambulance", "pharmacy",
    ],
    "waste": [
        "waste", "garbage", "trash", "bin", "bins", "landfill", "recycle",
        "recycling", "sanitation", "compost",
    ],
    "transport": [
        "traffic", "transport", "vehicle", "vehicles", "road", "signal",
        "signals", "congestion", "bus", "parking", "intersection", "commute",
        "commuting",
    ],
}

# Keyword hints per required-tech tag, restricted to the matching engine's fixed vocabulary.
TECH_KEYWORDS: Dict[str, List[str]] = {
    "iot": ["iot", "internet of things", "sensor node", "sensor network"],
    "sensors": ["sensor", "sensors", "acoustic", "pressure sensor", "ultrasonic"],
    "ai": ["ai", "artificial intelligence", "machine learning", "predictive model", "anomaly detection"],
    "computer-vision": ["camera", "cameras", "cctv", "video analytics", "computer vision", "image recognition"],
    "analytics": ["analytics", "dashboard", "data analysis", "telemetry data"],
    "cloud": ["cloud"],
    "mobile-app": ["mobile app", "smartphone app", "citizen app"],
    "gis": ["gis", "geospatial", "map dashboard", "mapping"],
    "telematics": ["telematics", "fleet tracking", "vehicle tracking", "gps tracking"],
    "robotics": ["robot", "robots", "robotic", "robotics", "drone", "drones"],
    "edge-computing": ["edge computing", "edge device", "edge ai"],
    "automation": ["automation", "automated", "automatic"],
}


def suggest_sector_and_tech(raw_description: str, title: str = "") -> Dict[str, Any]:
    """
    Returns {"sector": "water" | ... | None, "required_tech": [subset of TECH_VOCABULARY]}

    `sector` is None when no keyword matched at all (caller should leave the
    officer's current selection untouched rather than guess). `required_tech` can
    be an empty list for the same reason.
    """
    text = f"{title or ''} {raw_description or ''}".lower()

    sector_scores = {
        sector: sum(1 for kw in keywords if _contains_keyword(text, kw))
        for sector, keywords in SECTOR_KEYWORDS.items()
    }
    best_sector: Optional[str] = max(sector_scores, key=sector_scores.get)
    if sector_scores[best_sector] == 0:
        best_sector = None

    matched_tech = [
        tag for tag in TECH_VOCABULARY
        if any(_contains_keyword(text, kw) for kw in TECH_KEYWORDS.get(tag, []))
    ]

    return {"sector": best_sector, "required_tech": matched_tech}
