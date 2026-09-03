import pytest
from app.engines.performance import (
    achievement,
    achievement_percentage,
    final_score,
)


def test_achievement_lower_is_better():
    # Water wastage: baseline 30, target 20
    kpi_on_target = {
        "baseline": 30,
        "target": 20,
        "achieved": 20,
        "direction": "lower_is_better",
    }
    assert achievement(kpi_on_target) == 1.0
    assert achievement_percentage(kpi_on_target) == 100.0

    # Improved beyond target: achieved 17 -> gain 13 / span 10 = 1.3 -> capped at 1.2
    kpi_improved = {
        "baseline": 30,
        "target": 20,
        "achieved": 17,
        "direction": "lower_is_better",
    }
    assert achievement(kpi_improved) == 1.2
    assert achievement_percentage(kpi_improved) == 120.0

    # Moved wrong way: achieved 35 (got worse) -> gain is negative -> clamped to 0.0
    kpi_worse = {
        "baseline": 30,
        "target": 20,
        "achieved": 35,
        "direction": "lower_is_better",
    }
    assert achievement(kpi_worse) == 0.0
    assert achievement_percentage(kpi_worse) == 0.0


def test_achievement_higher_is_better():
    # System uptime: baseline 0, target 95
    kpi_perfect = {
        "baseline": 0,
        "target": 95,
        "achieved": 95,
        "direction": "higher_is_better",
    }
    assert achievement(kpi_perfect) == 1.0

    kpi_zero = {
        "baseline": 0,
        "target": 95,
        "achieved": 0,
        "direction": "higher_is_better",
    }
    assert achievement(kpi_zero) == 0.0


def test_achievement_overachievement_cap():
    # 400% overshoot: baseline 100, target 80, achieved 0 (gain 100 / span 20 = 5.0)
    kpi_huge = {
        "baseline": 100,
        "target": 80,
        "achieved": 0,
        "direction": "lower_is_better",
    }
    assert achievement(kpi_huge) == 1.2
    assert achievement_percentage(kpi_huge) == 120.0


def test_achievement_zero_span_no_division_by_zero():
    kpi_zero_span = {
        "baseline": 50,
        "target": 50,
        "achieved": 50,
        "direction": "higher_is_better",
    }
    assert achievement(kpi_zero_span) == 1.0


def test_final_score_roadmap_worked_example():
    """
    Validates Roadmap Section 7b worked example producing 92.9 exactly:
      - technical: detection time 67, uptime 91 -> 79.0 (30% weight -> 23.7)
      - cost: cost per km 87 -> 87.0 (20% weight -> 17.4)
      - impact: water wastage 120 -> 120.0 (20% weight -> 24.0)
      - scalability: districts ready 92, install time 86 -> 89.0 (15% weight -> 13.35)
      - security: checklist score 96 -> 96.0 (15% weight -> 14.4)
      Total = 23.7 + 17.4 + 24.0 + 13.35 + 14.4 = 92.85 -> 92.9
    """
    kpis = [
        {"category": "technical", "achievement": 67.0},
        {"category": "technical", "achievement": 91.0},
        {"category": "cost", "achievement": 87.0},
        {"category": "impact", "achievement": 120.0},
        {"category": "scalability", "achievement": 92.0},
        {"category": "scalability", "achievement": 86.0},
    ]
    security_score = 96.0

    res = final_score(kpis, security_score)

    assert res["category_scores"]["technical"] == 79.0
    assert res["category_scores"]["cost"] == 87.0
    assert res["category_scores"]["impact"] == 120.0
    assert res["category_scores"]["scalability"] == 89.0
    assert res["category_scores"]["security"] == 96.0
    assert res["final_score"] == 92.9


def test_final_score_empty_category_graceful():
    # If a category has no KPIs, it uses default 100.0 without crashing
    kpis = [
        {"category": "technical", "achievement": 80.0},
        {"category": "impact", "achievement": 90.0},
    ]
    res = final_score(kpis, security_score=85.0)
    assert "category_scores" in res
    assert res["category_scores"]["technical"] == 80.0
    assert res["category_scores"]["impact"] == 90.0
    assert res["category_scores"]["security"] == 85.0
    assert isinstance(res["final_score"], float)
