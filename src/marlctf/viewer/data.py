"""Viewer artifact discovery, parsing, and validation helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from marlctf.replay import ReplayValidationResult, validate_replay_sequence


class ViewerDataError(RuntimeError):
    """Raised when viewer input cannot be loaded or parsed."""


@dataclass(frozen=True)
class ValidationResult:
    """Validation result for viewer-facing artifact checks."""

    ok: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ViewerManifest:
    """Visualizable artifacts discovered from a local path."""

    source_path: Path
    run_metadata: dict[str, Any] | None = None
    replay_artifacts: tuple[Path, ...] = ()
    metric_artifacts: tuple[Path, ...] = ()
    comparison_artifact: Path | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReplayArtifactData:
    """Loaded replay snapshots and validation details."""

    path: Path
    snapshots: tuple[dict[str, Any], ...]
    validation: ValidationResult


def load_viewer_manifest(path: str | Path) -> ViewerManifest:
    """Discover viewer-readable artifacts from a run directory or artifact file."""

    source_path = Path(path)
    if not source_path.exists():
        raise ViewerDataError(f"selected artifact does not exist: {source_path}")

    if source_path.is_file():
        return _manifest_from_file(source_path)

    run_metadata: dict[str, Any] | None = None
    warnings: list[str] = []
    run_path = source_path / "run.json"
    if run_path.exists():
        run_metadata = load_json_artifact(run_path)
    else:
        warnings.append("run.json not found")

    replay_artifacts = _discover_replay_paths(source_path, run_metadata)
    metric_artifacts = tuple(path for path in (source_path / "metrics.jsonl",) if path.exists())
    comparison_path = source_path / "comparison.json"
    comparison_artifact = comparison_path if comparison_path.exists() else None

    if not replay_artifacts:
        warnings.append("no replay artifacts found")
    if not metric_artifacts:
        warnings.append("no metrics artifacts found")

    return ViewerManifest(
        source_path=source_path,
        run_metadata=run_metadata,
        replay_artifacts=tuple(replay_artifacts),
        metric_artifacts=metric_artifacts,
        comparison_artifact=comparison_artifact,
        warnings=tuple(warnings),
    )


def load_replay_artifact(path: str | Path) -> ReplayArtifactData:
    """Load and validate a replay JSONL artifact."""

    artifact_path = Path(path)
    snapshots = tuple(load_jsonl_artifact(artifact_path))
    validation = _to_viewer_validation(validate_replay_sequence(snapshots))
    return ReplayArtifactData(path=artifact_path, snapshots=snapshots, validation=validation)


def load_json_artifact(path: str | Path) -> dict[str, Any]:
    """Load a JSON object artifact with viewer-friendly errors."""

    artifact_path = Path(path)
    if not artifact_path.exists():
        raise ViewerDataError(f"JSON artifact does not exist: {artifact_path}")
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ViewerDataError(f"malformed JSON artifact: {artifact_path}") from exc
    if not isinstance(payload, dict):
        raise ViewerDataError(f"JSON artifact must contain an object: {artifact_path}")
    return payload


def load_jsonl_artifact(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSONL artifact as a list of objects with line-aware errors."""

    artifact_path = Path(path)
    if not artifact_path.exists():
        raise ViewerDataError(f"JSONL artifact does not exist: {artifact_path}")

    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(artifact_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ViewerDataError(f"malformed JSONL at {artifact_path}:{line_no}") from exc
        if not isinstance(payload, dict):
            raise ViewerDataError(f"JSONL row must contain an object at {artifact_path}:{line_no}")
        rows.append(payload)
    return rows


def _manifest_from_file(source_path: Path) -> ViewerManifest:
    warnings: list[str] = []
    replay_artifacts: tuple[Path, ...] = ()
    metric_artifacts: tuple[Path, ...] = ()
    comparison_artifact: Path | None = None

    if source_path.suffix == ".jsonl":
        if source_path.name.startswith("replay") or source_path.parent.name == "replays":
            replay_artifacts = (source_path,)
        else:
            metric_artifacts = (source_path,)
    elif source_path.name == "comparison.json":
        comparison_artifact = source_path
    elif source_path.name == "run.json":
        return load_viewer_manifest(source_path.parent)
    else:
        warnings.append(f"unrecognized viewer artifact file: {source_path.name}")

    return ViewerManifest(
        source_path=source_path,
        replay_artifacts=replay_artifacts,
        metric_artifacts=metric_artifacts,
        comparison_artifact=comparison_artifact,
        warnings=tuple(warnings),
    )


def _discover_replay_paths(root: Path, run_metadata: dict[str, Any] | None) -> list[Path]:
    paths: list[Path] = []
    if run_metadata:
        for raw_path in run_metadata.get("replay_paths", []):
            candidate = Path(raw_path)
            if not candidate.is_absolute():
                if candidate.exists():
                    candidate = candidate.resolve()
                else:
                    candidate = root / candidate
            if candidate.exists() and candidate not in paths:
                paths.append(candidate)

        for sample in run_metadata.get("sampled_replays", []):
            raw_path = sample.get("path") if isinstance(sample, dict) else None
            if not raw_path:
                continue
            candidate = Path(raw_path)
            if not candidate.is_absolute():
                candidate = root / candidate
            if candidate.exists() and candidate not in paths:
                paths.append(candidate)

    default_replay = root / "replay.jsonl"
    if default_replay.exists() and default_replay not in paths:
        paths.append(default_replay)

    replay_dir = root / "replays"
    if replay_dir.exists():
        for candidate in sorted(replay_dir.glob("*.jsonl")):
            if candidate not in paths:
                paths.append(candidate)

    return paths


def _to_viewer_validation(result: ReplayValidationResult) -> ValidationResult:
    return ValidationResult(ok=result.ok, errors=result.errors, warnings=result.warnings)
