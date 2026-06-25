from __future__ import annotations

import json

from marlctf.cli import main


def test_match_cli_writes_required_artifacts(tmp_path):
    artifact_dir = tmp_path / "match"
    exit_code = main(
        [
            "match",
            "--config",
            "configs/smoke_match.yml",
            "--seed",
            "42",
            "--artifact-dir",
            artifact_dir.as_posix(),
        ]
    )

    assert exit_code == 0
    assert (artifact_dir / "run.json").exists()
    assert (artifact_dir / "metrics.jsonl").exists()
    assert (artifact_dir / "events.jsonl").exists()
    run = json.loads((artifact_dir / "run.json").read_text(encoding="utf-8"))
    assert run["status"] == "completed"
    assert run["run_type"] == "match"


def test_match_cli_returns_config_error_for_missing_config(tmp_path):
    exit_code = main(
        [
            "match",
            "--config",
            (tmp_path / "missing.yml").as_posix(),
            "--artifact-dir",
            (tmp_path / "out").as_posix(),
        ]
    )

    assert exit_code == 1
