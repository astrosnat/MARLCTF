from __future__ import annotations

import json

from marlctf.evaluation.evaluator import run_evaluation


def test_evaluation_smoke_writes_per_seed_metrics_and_comparison(tmp_path):
    artifact_dir = tmp_path / "eval"

    result = run_evaluation("configs/smoke_eval.yml", artifact_dir=artifact_dir)

    assert result["status"] == "completed"
    assert result["run_type"] == "evaluate"
    assert result["summary"]["seed_count"] == 10
    assert (artifact_dir / "run.json").exists()
    assert (artifact_dir / "metrics.jsonl").exists()
    assert (artifact_dir / "comparison.json").exists()

    metrics = (artifact_dir / "metrics.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(metrics) == 10
    first_metric = json.loads(metrics[0])
    assert {
        "seed",
        "winner",
        "score",
        "returns",
        "episode_length",
        "rule_validity_failures",
    } <= set(first_metric)

    comparison = json.loads((artifact_dir / "comparison.json").read_text(encoding="utf-8"))
    assert comparison["candidate"]["team"] == "red"
    assert comparison["baseline"]["team"] == "blue"
    assert "win_rate" in comparison["candidate"]["metrics"]
    assert "passed" in comparison["acceptance"]


def test_evaluation_accepts_policy_overrides(tmp_path):
    artifact_dir = tmp_path / "eval"

    result = run_evaluation(
        "configs/smoke_eval.yml",
        artifact_dir=artifact_dir,
        candidate="random",
        baseline="scripted",
    )

    assert result["status"] == "completed"
    assert result["policy_ids"] == ["red:random", "blue:scripted"]
