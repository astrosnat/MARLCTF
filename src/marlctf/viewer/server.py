"""Small local HTTP server for the static MARLCTF viewer."""

from __future__ import annotations

import json
import mimetypes
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from marlctf.viewer.data import ViewerDataError, load_replay_artifact, load_viewer_manifest


@dataclass(frozen=True)
class ViewerServer:
    """Created viewer server and resolved URL."""

    httpd: ThreadingHTTPServer
    url: str
    artifact: Path | None = None


def create_viewer_server(
    *,
    artifact: str | Path | None = None,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> ViewerServer:
    """Create a local HTTP server for viewer static files and artifact data."""

    artifact_path = Path(artifact) if artifact is not None else None
    static_root = resources.files("marlctf.viewer").joinpath("static")

    class ViewerRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - http.server hook
            parsed = urlparse(self.path)
            if parsed.path == "/api/artifact":
                self._serve_artifact()
                return
            self._serve_static(parsed.path)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return None

        def _serve_artifact(self) -> None:
            if artifact_path is None:
                self._send_json({"manifest": None, "replay": None, "warnings": ["no artifact selected"]})
                return
            try:
                manifest = load_viewer_manifest(artifact_path)
                replay_payload = None
                if manifest.replay_artifacts:
                    replay = load_replay_artifact(manifest.replay_artifacts[0])
                    replay_payload = {
                        "path": replay.path.as_posix(),
                        "snapshots": list(replay.snapshots),
                        "validation": {
                            "ok": replay.validation.ok,
                            "errors": list(replay.validation.errors),
                            "warnings": list(replay.validation.warnings),
                        },
                    }
                self._send_json(
                    {
                        "manifest": {
                            "source_path": manifest.source_path.as_posix(),
                            "run_metadata": manifest.run_metadata,
                            "replay_artifacts": [path.as_posix() for path in manifest.replay_artifacts],
                            "metric_artifacts": [path.as_posix() for path in manifest.metric_artifacts],
                            "comparison_artifact": (
                                None if manifest.comparison_artifact is None else manifest.comparison_artifact.as_posix()
                            ),
                            "warnings": list(manifest.warnings),
                        },
                        "replay": replay_payload,
                    }
                )
            except ViewerDataError as exc:
                self._send_json({"error": str(exc)}, status=400)

        def _serve_static(self, request_path: str) -> None:
            relative = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
            if "/" in relative:
                self.send_error(404)
                return
            try:
                resource = static_root.joinpath(relative)
                data = resource.read_bytes()
            except (FileNotFoundError, IsADirectoryError):
                self.send_error(404)
                return
            content_type = mimetypes.guess_type(relative)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    httpd = ThreadingHTTPServer((host, port), ViewerRequestHandler)
    actual_host, actual_port = httpd.server_address[:2]
    return ViewerServer(httpd=httpd, url=f"http://{actual_host}:{actual_port}", artifact=artifact_path)


def run_viewer(
    *,
    artifact: str | Path | None = None,
    host: str = "127.0.0.1",
    port: int = 8000,
    open_browser: bool = True,
) -> int:
    """Run the viewer server until interrupted."""

    server = create_viewer_server(artifact=artifact, host=host, port=port)
    print(f"MARLCTF viewer: {server.url}")
    if artifact is not None:
        print(f"Artifact: {Path(artifact).as_posix()}")
    else:
        print("No artifact selected. Use --artifact <run-dir-or-file> to preload replay data.")
    if open_browser:
        webbrowser.open(server.url)
    try:
        server.httpd.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.httpd.server_close()
    return 0
