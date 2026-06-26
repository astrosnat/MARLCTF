from __future__ import annotations

import json

import pytest

from marlctf.env.mechanics import create_initial_match
from marlctf.replay import build_replay_snapshot
from marlctf.viewer.data import (
    ViewerDataError,
    load_json_artifact,
    load_jsonl_artifact,
    load_replay_artifact,
    load_viewer_manifest,
)


def test_viewer_manifest_discovers_run_directory_artifacts(tmp_path, smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    snapshot = build_replay_snapshot(match, smoke_scenario)
    (tmp_path / "run.json").write_text(
        json.dumps(
            {
                "run_id": snapshot["run_id"],
                "scenario_id": smoke_scenario.scenario_id,
                "replay_paths": ["replay.jsonl"],
                "metrics_path": "metrics.jsonl",
                "comparison_path": "comparison.json",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "replay.jsonl").write_text(json.dumps(snapshot) + "\n", encoding="utf-8")
    (tmp_path / "metrics.jsonl").write_text(json.dumps({"episode": 1, "episode_return": 1.0}) + "\n", encoding="utf-8")
    (tmp_path / "comparison.json").write_text(json.dumps({"acceptance": {"passed": True}}), encoding="utf-8")

    manifest = load_viewer_manifest(tmp_path)

    assert manifest.run_metadata is not None
    assert manifest.replay_artifacts == (tmp_path / "replay.jsonl",)
    assert manifest.metric_artifacts == (tmp_path / "metrics.jsonl",)
    assert manifest.comparison_artifact == tmp_path / "comparison.json"
    assert manifest.warnings == ()


def test_viewer_manifest_accepts_direct_replay_metrics_and_comparison_files(tmp_path):
    replay = tmp_path / "replay.jsonl"
    metrics = tmp_path / "metrics.jsonl"
    comparison = tmp_path / "comparison.json"
    replay.write_text("", encoding="utf-8")
    metrics.write_text("", encoding="utf-8")
    comparison.write_text("{}", encoding="utf-8")

    assert load_viewer_manifest(replay).replay_artifacts == (replay,)
    assert load_viewer_manifest(metrics).metric_artifacts == (metrics,)
    assert load_viewer_manifest(comparison).comparison_artifact == comparison


def test_viewer_manifest_warns_for_missing_optional_artifacts(tmp_path):
    (tmp_path / "run.json").write_text(json.dumps({"run_id": "run-1"}), encoding="utf-8")

    manifest = load_viewer_manifest(tmp_path)

    assert manifest.replay_artifacts == ()
    assert manifest.metric_artifacts == ()
    assert "no replay artifacts found" in manifest.warnings
    assert "no metrics artifacts found" in manifest.warnings


def test_viewer_loads_json_jsonl_and_validates_replay(tmp_path, smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    snapshot = build_replay_snapshot(match, smoke_scenario)
    replay = tmp_path / "replay.jsonl"
    replay.write_text(json.dumps(snapshot) + "\n", encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"name": "viewer"}), encoding="utf-8")

    assert load_json_artifact(config) == {"name": "viewer"}
    assert load_jsonl_artifact(replay)[0]["step"] == 0
    replay_data = load_replay_artifact(replay)
    assert replay_data.validation.ok
    assert replay_data.snapshots[0]["schema_version"] == "1.0"


def test_viewer_replay_validation_reports_missing_required_fields(tmp_path):
    replay = tmp_path / "replay.jsonl"
    replay.write_text(json.dumps({"schema_version": "1.0"}) + "\n", encoding="utf-8")

    replay_data = load_replay_artifact(replay)

    assert not replay_data.validation.ok
    assert any("missing required field" in error for error in replay_data.validation.errors)


def test_viewer_data_errors_are_clear_for_missing_and_malformed_files(tmp_path):
    with pytest.raises(ViewerDataError, match="does not exist"):
        load_viewer_manifest(tmp_path / "missing")

    malformed = tmp_path / "metrics.jsonl"
    malformed.write_text("{not-json}\n", encoding="utf-8")
    with pytest.raises(ViewerDataError, match="malformed JSONL"):
        load_jsonl_artifact(malformed)
