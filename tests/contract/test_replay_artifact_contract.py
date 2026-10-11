from __future__ import annotations

import json

from marlctf.replay import validate_replay_sequence
from marlctf.runner import run_match


REQUIRED_FIELDS = {
    "schema_version",
    "run_id",
    "run_type",
    "scenario_id",
    "seed",
    "step",
    "map",
    "agents",
    "flags",
    "score",
    "terminal",
    "events",
}


def test_match_replay_artifact_contains_required_fields_and_final_state(tmp_path):
    artifact_dir = tmp_path / "match"
    run = run_match("configs/smoke_match.yml", seed=42, artifact_dir=artifact_dir)

    replay_path = artifact_dir / "replay.jsonl"
    assert replay_path.exists()
    snapshots = [
        json.loads(line)
        for line in replay_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert snapshots
    assert validate_replay_sequence(snapshots).ok
    for snapshot in snapshots:
        assert REQUIRED_FIELDS <= set(snapshot)
        assert set(snapshot["agents"]) == {"red_0", "red_1", "red_2", "blue_0", "blue_1", "blue_2"}
        assert set(snapshot["flags"]) == {"red", "blue"}
        assert set(snapshot["score"]) == {"red", "blue"}

    final = snapshots[-1]
    assert final["run_id"] == run["run_id"]
    assert final["step"] == run["summary"]["steps"]
    assert final["score"] == run["summary"]["score"]
    assert final["terminal"]["status"] == run["summary"]["status"]
    assert final["terminal"]["winner"] == run["summary"]["winner"]
    assert final["terminal"]["reason"] == run["summary"]["terminal_reason"]


def test_match_run_json_records_replay_discoverability(tmp_path):
    artifact_dir = tmp_path / "match"
    run_match("configs/smoke_match.yml", seed=42, artifact_dir=artifact_dir)

    run = json.loads((artifact_dir / "run.json").read_text(encoding="utf-8"))

    assert run["replay_available"] is True
    assert run["replay_paths"] == [(artifact_dir / "replay.jsonl").as_posix()]
