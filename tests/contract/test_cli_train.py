from __future__ import annotations

import json

from marlctf.cli import main


def test_train_cli_writes_required_artifacts(tmp_path):
    artifact_dir = tmp_path / "train"
    exit_code = main(
        [
            "train",
            "--config",
            "configs/smoke_train.yml",
            "--seed",
            "7",
            "--artifact-dir",
            artifact_dir.as_posix(),
            "--episodes",
            "3",
        ]
    )

    assert exit_code == 0
    assert (artifact_dir / "run.json").exists()
    assert (artifact_dir / "metrics.jsonl").exists()
    assert (artifact_dir / "checkpoints" / "latest.pt").exists()
    run = json.loads((artifact_dir / "run.json").read_text(encoding="utf-8"))
    assert run["status"] == "completed"
    assert run["run_type"] == "train"


def test_train_cli_returns_config_error_for_missing_config(tmp_path):
    exit_code = main(
        [
            "train",
            "--config",
            (tmp_path / "missing.yml").as_posix(),
            "--artifact-dir",
            (tmp_path / "out").as_posix(),
        ]
    )

    assert exit_code == 1
