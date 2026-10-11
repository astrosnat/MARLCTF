from __future__ import annotations

import json

from marlctf.artifacts import RunArtifactWriter, read_json, read_jsonl
from marlctf.env.mechanics import create_initial_match
from marlctf.replay import build_replay_snapshot


def test_artifact_writer_appends_replay_snapshots_and_records_metadata(
    tmp_path,
    sample_run_metadata,
    smoke_scenario,
):
    writer = RunArtifactWriter(tmp_path, sample_run_metadata)
    match = create_initial_match(smoke_scenario, seed=42)
    first = build_replay_snapshot(match, smoke_scenario, step=0)
    second = build_replay_snapshot(match, smoke_scenario, step=1)

    replay_path = writer.append_replay_snapshot(first)
    writer.append_replay_snapshot(second)

    assert replay_path == tmp_path / "replay.jsonl"
    rows = read_jsonl(replay_path)
    assert [row["step"] for row in rows] == [0, 1]

    run = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    assert run["replay_available"] is True
    assert run["replay_paths"] == [(tmp_path / "replay.jsonl").as_posix()]


def test_artifact_writer_supports_custom_replay_path_and_generic_jsonl(
    tmp_path,
    sample_run_metadata,
    smoke_scenario,
):
    writer = RunArtifactWriter(tmp_path, sample_run_metadata)
    match = create_initial_match(smoke_scenario, seed=42)
    snapshot = build_replay_snapshot(match, smoke_scenario)

    replay_path = writer.append_replay_snapshot(snapshot, "replays/episode-000001.jsonl")
    metrics_path = writer.append_jsonl_artifact("viewer/custom.jsonl", {"kind": "viewer"})

    assert replay_path == tmp_path / "replays" / "episode-000001.jsonl"
    assert read_jsonl(replay_path)[0]["schema_version"] == "1.0"
    assert read_jsonl(metrics_path) == [{"kind": "viewer"}]

    run = read_json(tmp_path / "run.json")
    assert run["replay_paths"] == [replay_path.as_posix()]


def test_artifact_writer_can_clear_replay_metadata(tmp_path, sample_run_metadata):
    writer = RunArtifactWriter(tmp_path, sample_run_metadata)

    writer.set_replay_paths([])

    run = read_json(tmp_path / "run.json")
    assert run["replay_available"] is False
    assert run["replay_paths"] == []
