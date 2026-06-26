from __future__ import annotations

import json
import threading
import urllib.request

from marlctf.runner import run_match
from marlctf.viewer.server import create_viewer_server


def test_viewer_server_serves_static_shell_and_replay_payload(tmp_path):
    artifact_dir = tmp_path / "match"
    run_match("configs/smoke_match.yml", seed=42, artifact_dir=artifact_dir)
    server = create_viewer_server(artifact=artifact_dir, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.httpd.serve_forever, daemon=True)
    thread.start()

    try:
        index = urllib.request.urlopen(server.url, timeout=5).read().decode("utf-8")
        payload = json.loads(
            urllib.request.urlopen(f"{server.url}/api/artifact", timeout=5)
            .read()
            .decode("utf-8")
        )
    finally:
        server.httpd.shutdown()
        thread.join(timeout=5)

    assert "replay-canvas" in index
    assert payload["manifest"]["replay_artifacts"]
    assert payload["replay"]["validation"]["ok"] is True
    assert payload["replay"]["snapshots"][0]["step"] == 0
