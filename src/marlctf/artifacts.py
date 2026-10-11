"""Local JSON/JSONL artifact writing."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from marlctf.models import RunStatus


class ArtifactError(RuntimeError):
    """Raised when artifact output cannot be written."""


class RunArtifactWriter:
    """Writes run metadata, metrics, events, and replay artifacts."""

    def __init__(self, artifact_dir: str | Path, metadata: dict[str, Any]) -> None:
        self.artifact_dir = Path(artifact_dir)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.run_path = self.artifact_dir / "run.json"
        self.metrics_path = self.artifact_dir / "metrics.jsonl"
        self.events_path = self.artifact_dir / "events.jsonl"
        self.replay_path = self.artifact_dir / "replay.jsonl"
        self.metadata = {
            "created_at": datetime.now(UTC).isoformat(),
            "status": RunStatus.RUNNING.value,
            **metadata,
            "metrics_path": self.metrics_path.as_posix(),
            "events_path": self.events_path.as_posix(),
        }
        self._write_run()

    def append_metric(self, metric: dict[str, Any]) -> None:
        self._append_jsonl(self.metrics_path, metric)

    def append_event(self, event: dict[str, Any]) -> None:
        self._append_jsonl(self.events_path, event)

    def append_replay_snapshot(self, snapshot: dict[str, Any], path: str | Path | None = None) -> Path:
        replay_path = self._artifact_path(path) if path is not None else self.replay_path
        replay_path.parent.mkdir(parents=True, exist_ok=True)
        self._append_jsonl(replay_path, snapshot)
        existing_paths = [Path(item) for item in self.metadata.get("replay_paths", [])]
        if replay_path not in existing_paths:
            existing_paths.append(replay_path)
        self.set_replay_paths(existing_paths)
        return replay_path

    def append_jsonl_artifact(self, filename: str, payload: dict[str, Any]) -> Path:
        path = self._artifact_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._append_jsonl(path, payload)
        return path

    def set_checkpoint_paths(self, checkpoint_paths: list[str | Path]) -> None:
        self.metadata["checkpoint_paths"] = [Path(path).as_posix() for path in checkpoint_paths]
        self._write_run()

    def set_replay_paths(self, replay_paths: list[str | Path]) -> None:
        self.metadata["replay_paths"] = [Path(path).as_posix() for path in replay_paths]
        self.metadata["replay_available"] = bool(replay_paths)
        self._write_run()

    def write_json_artifact(self, filename: str, payload: dict[str, Any]) -> Path:
        path = self._artifact_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.metadata[f"{path.stem}_path"] = path.as_posix()
        self._write_run()
        return path

    def complete(self, summary: dict[str, Any]) -> dict[str, Any]:
        if not summary:
            raise ArtifactError("completed runs require summary metrics")
        self.metadata["status"] = RunStatus.COMPLETED.value
        self.metadata["summary"] = summary
        self.metadata.pop("error", None)
        self._write_run()
        return dict(self.metadata)

    def fail(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> dict[str, Any]:
        self.metadata["status"] = RunStatus.FAILED.value
        self.metadata["error"] = {"code": code, "message": message, "details": details or {}}
        self._write_run()
        return dict(self.metadata)

    def interrupted(self, reason: str) -> dict[str, Any]:
        self.metadata["status"] = RunStatus.INTERRUPTED.value
        self.metadata["error"] = {"code": "interrupted", "message": reason, "details": {}}
        self._write_run()
        return dict(self.metadata)

    def _artifact_path(self, path: str | Path) -> Path:
        artifact_path = Path(path)
        if artifact_path.is_absolute():
            return artifact_path
        return self.artifact_dir / artifact_path

    def _write_run(self) -> None:
        self.run_path.write_text(
            json.dumps(_jsonable(self.metadata), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _append_jsonl(self, path: Path, payload: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_jsonable(payload), sort_keys=True) + "\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read a JSONL artifact file."""

    artifact_path = Path(path)
    if not artifact_path.exists():
        return []
    return [
        json.loads(line)
        for line in artifact_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def read_json(path: str | Path) -> dict[str, Any]:
    """Read a JSON object artifact file."""

    artifact_path = Path(path)
    if not artifact_path.exists():
        return {}
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ArtifactError(f"JSON artifact must contain an object: {artifact_path}")
    return payload


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    return value
