from __future__ import annotations

from marlctf.evaluation.metrics import build_comparison, summarize_team_results


def test_summarize_team_results_calculates_aggregate_metrics():
    results = [
        {
            "seed": 101,
            "winner": "red",
            "score": {"red": 1, "blue": 0},
            "returns": {"red": 12.0, "blue": -8.0},
            "episode_length": 20,
            "rule_validity_failures": 0,
        },
        {
            "seed": 102,
            "winner": "blue",
            "score": {"red": 0, "blue": 1},
            "returns": {"red": -4.0, "blue": 11.0},
            "episode_length": 40,
            "rule_validity_failures": 1,
        },
    ]

    summary = summarize_team_results(results, "red")

    assert summary == {
        "seed_count": 2,
        "win_rate": 0.5,
        "capture_count": 1,
        "average_return": 4.0,
        "average_episode_length": 30.0,
        "rule_validity_failures": 1,
    }


def test_build_comparison_reports_acceptance_threshold_result():
    results = [
        {
            "seed": 101,
            "winner": "red",
            "score": {"red": 1, "blue": 0},
            "returns": {"red": 12.0, "blue": -8.0},
            "episode_length": 20,
            "rule_validity_failures": 0,
        },
        {
            "seed": 102,
            "winner": "draw",
            "score": {"red": 0, "blue": 0},
            "returns": {"red": -2.0, "blue": -2.0},
            "episode_length": 200,
            "rule_validity_failures": 0,
        },
    ]

    comparison = build_comparison(
        results,
        candidate_team="red",
        baseline_team="blue",
        acceptance={"min_win_rate": 0.5, "max_rule_validity_failures": 0},
    )

    assert comparison["candidate"]["metrics"]["win_rate"] == 0.5
    assert comparison["baseline"]["metrics"]["win_rate"] == 0.0
    assert comparison["acceptance"] == {
        "min_win_rate": 0.5,
        "max_rule_validity_failures": 0,
        "passed": True,
    }
