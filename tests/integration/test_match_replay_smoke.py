from __future__ import annotations

import json

from marlctf.runner import run_match


def test_match_replay_smoke_writes_initial_step_terminal_and_small_artifact(tmp_path):
    artifact_dir = tmp_path / "match"

    run = run_match("configs/smoke_match.yml", seed=42, artifact_dir=artifact_dir)

    replay_path = artifact_dir / "replay.jsonl"
    snapshots = [
        json.loads(line)
        for line in replay_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    steps = [snapshot["step"] for snapshot in snapshots]

    assert steps[0] == 0
    assert steps[-1] == run["summary"]["steps"]
    assert steps == sorted(steps)
    assert len(snapshots) == run["summary"]["steps"] + 1
    assert snapshots[0]["events"] == []
    assert snapshots[-1]["terminal"]["status"] in {"terminated", "truncated"}
    assert replay_path.stat().st_size < 1_000_000
