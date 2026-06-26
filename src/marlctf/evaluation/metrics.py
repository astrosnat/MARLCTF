"""Aggregate metrics for fixed-seed policy evaluations."""

from __future__ import annotations

from typing import Any


def summarize_team_results(results: list[dict[str, Any]], team_id: str) -> dict[str, Any]:
    """Summarize per-seed match results from one team's perspective."""

    if not results:
        return {
            "seed_count": 0,
            "win_rate": 0.0,
            "capture_count": 0,
            "average_return": 0.0,
            "average_episode_length": 0.0,
            "rule_validity_failures": 0,
        }

    seed_count = len(results)
    wins = sum(1 for result in results if result["winner"] == team_id)
    capture_count = sum(int(result["score"].get(team_id, 0)) for result in results)
    total_return = sum(float(result["returns"].get(team_id, 0.0)) for result in results)
    total_length = sum(int(result["episode_length"]) for result in results)
    rule_failures = sum(int(result.get("rule_validity_failures", 0)) for result in results)
    return {
        "seed_count": seed_count,
        "win_rate": round(wins / seed_count, 6),
        "capture_count": capture_count,
        "average_return": round(total_return / seed_count, 6),
        "average_episode_length": round(total_length / seed_count, 6),
        "rule_validity_failures": rule_failures,
    }


def build_comparison(
    results: list[dict[str, Any]],
    *,
    candidate_team: str,
    baseline_team: str,
    acceptance: dict[str, Any],
) -> dict[str, Any]:
    """Build baseline-versus-candidate aggregate evidence."""

    candidate_metrics = summarize_team_results(results, candidate_team)
    baseline_metrics = summarize_team_results(results, baseline_team)
    min_win_rate = float(acceptance.get("min_win_rate", 0.0))
    max_rule_failures = int(acceptance.get("max_rule_validity_failures", 0))
    passed = (
        candidate_metrics["win_rate"] >= min_win_rate
        and candidate_metrics["rule_validity_failures"] <= max_rule_failures
    )
    return {
        "candidate": {"team": candidate_team, "metrics": candidate_metrics},
        "baseline": {"team": baseline_team, "metrics": baseline_metrics},
        "acceptance": {
            "min_win_rate": min_win_rate,
            "max_rule_validity_failures": max_rule_failures,
            "passed": passed,
        },
    }
