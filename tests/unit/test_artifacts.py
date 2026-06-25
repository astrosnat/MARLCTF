from __future__ import annotations

import json

import pytest

from marlctf.artifacts import ArtifactError, RunArtifactWriter, read_jsonl


def test_artifact_writer_creates_run_metrics_and_events(tmp_path, sample_run_metadata):
    writer = RunArtifactWriter(tmp_path, sample_run_metadata)
    writer.append_metric({"step": 0, "red_score": 0, "blue_score": 0})
    writer.append_event({"step": 0, "event_type": "move", "agent_id": "red_0"})
    final = writer.complete({"winner": "red", "red_score": 1, "blue_score": 0})

    run = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    assert run["status"] == "completed"
    assert run["summary"]["winner"] == "red"
    assert final["summary"]["red_score"] == 1
    assert read_jsonl(tmp_path / "metrics.jsonl") == [{"blue_score": 0, "red_score": 0, "step": 0}]
    assert read_jsonl(tmp_path / "events.jsonl")[0]["event_type"] == "move"


def test_artifact_writer_requires_summary_for_completed_runs(tmp_path, sample_run_metadata):
    writer = RunArtifactWriter(tmp_path, sample_run_metadata)

    with pytest.raises(ArtifactError, match="summary"):
        writer.complete({})


def test_artifact_writer_records_failed_run(tmp_path, sample_run_metadata):
    writer = RunArtifactWriter(tmp_path, sample_run_metadata)
    writer.fail("config_error", "missing max_steps", details={"field": "max_steps"})

    run = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    assert run["status"] == "failed"
    assert run["error"]["code"] == "config_error"
    assert run["error"]["details"]["field"] == "max_steps"


def test_artifact_writer_records_interrupted_run(tmp_path, sample_run_metadata):
    writer = RunArtifactWriter(tmp_path, sample_run_metadata)
    writer.interrupted("keyboard interrupt")

    run = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    assert run["status"] == "interrupted"
    assert run["error"]["message"] == "keyboard interrupt"
