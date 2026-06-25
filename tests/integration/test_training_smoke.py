from __future__ import annotations

import json

from marlctf.training.runner import run_training


def test_training_smoke_writes_metrics_and_checkpoint(tmp_path):
    artifact_dir = tmp_path / "train"

    result = run_training(
        "configs/smoke_train.yml",
        seed=7,
        artifact_dir=artifact_dir,
        episodes=3,
    )

    assert result["status"] == "completed"
    assert result["summary"]["episodes"] == 3
    assert (artifact_dir / "run.json").exists()
    assert (artifact_dir / "metrics.jsonl").exists()
    assert (artifact_dir / "checkpoints" / "latest.pt").exists()

    metrics = (artifact_dir / "metrics.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(metrics) == 3
    first_metric = json.loads(metrics[0])
    assert {"episode", "episode_return", "winner", "capture_count", "episode_length"} <= set(first_metric)

    run = json.loads((artifact_dir / "run.json").read_text(encoding="utf-8"))
    assert run["algorithm"] == "vdn"
    assert run["checkpoint_paths"]
