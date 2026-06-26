from __future__ import annotations

from pathlib import Path


STATIC_ROOT = Path("src/marlctf/viewer/static")


def test_static_viewer_exposes_replay_canvas_controls_and_text_state():
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'id="replay-canvas"' in html
    assert 'id="play-button"' in html
    assert 'id="pause-button"' in html
    assert 'id="restart-button"' in html
    assert 'id="step-back-button"' in html
    assert 'id="step-forward-button"' in html
    assert 'id="speed-select"' in html
    assert 'id="step-scrubber"' in html
    assert 'id="event-list"' in html
    assert 'id="score-text"' in html
    assert 'id="terminal-text"' in html


def test_static_viewer_script_draws_replay_state_and_updates_controls():
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")

    assert "drawBoard" in script
    assert "renderSnapshot" in script
    assert "drawAgents" in script
    assert "drawFlags" in script
    assert "event-list" in script
    assert "step-scrubber" in script
    assert "/api/artifact" in script
