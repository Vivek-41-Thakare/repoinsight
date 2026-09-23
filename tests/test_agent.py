from app.planner import Planner


def test_planner_fallback_plan():
    planner = Planner()

    plan = planner._fallback_plan()

    assert isinstance(plan, list)
    assert len(plan) >= 5
    assert "Validate the GitHub repository" in plan
    assert "Generate a structured final report" in plan
