from __future__ import annotations

import json

from marlctf.cli import main
from marlctf.runner import run_match


def test_match_cli_writes_replay_metadata(tmp_path):
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
    assert (artifact_dir / "replay.jsonl").exists()
    run = json.loads((artifact_dir / "run.json").read_text(encoding="utf-8"))
    assert run["replay_available"] is True
    assert run["replay_paths"] == [(artifact_dir / "replay.jsonl").as_posix()]


def test_viewer_cli_accepts_valid_artifact(monkeypatch, tmp_path):
    artifact_dir = tmp_path / "match"
    run_match("configs/smoke_match.yml", seed=42, artifact_dir=artifact_dir)
    calls: list[dict[str, object]] = []

    def fake_run_viewer(**kwargs):
        calls.append(kwargs)
        return 0

    monkeypatch.setattr("marlctf.cli.run_viewer", fake_run_viewer)

    exit_code = main(
        [
            "viewer",
            "--artifact",
            artifact_dir.as_posix(),
            "--host",
            "127.0.0.1",
            "--port",
            "0",
            "--no-open",
        ]
    )

    assert exit_code == 0
    assert calls == [
        {
            "artifact": artifact_dir,
            "host": "127.0.0.1",
            "port": 0,
            "open_browser": False,
        }
    ]


def test_viewer_cli_returns_user_error_for_missing_artifact(tmp_path):
    exit_code = main(
        [
            "viewer",
            "--artifact",
            (tmp_path / "missing").as_posix(),
            "--no-open",
        ]
    )

    assert exit_code == 1
