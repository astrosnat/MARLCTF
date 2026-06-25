from __future__ import annotations

import json

from marlctf.runner import run_match


def test_seeded_scripted_match_is_reproducible(tmp_path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first = run_match("configs/smoke_match.yml", seed=42, artifact_dir=first_dir)
    second = run_match("configs/smoke_match.yml", seed=42, artifact_dir=second_dir)

    assert first["summary"]["winner"] == second["summary"]["winner"]
    assert first["summary"]["score"] == second["summary"]["score"]
    first_events = (first_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
    second_events = (second_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
    assert first_events == second_events

    run = json.loads((first_dir / "run.json").read_text(encoding="utf-8"))
    assert run["summary"]["terminal_reason"] in {"capture_target", "max_steps"}
