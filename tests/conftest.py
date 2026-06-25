"""Shared test fixtures for MARLCTF."""

from __future__ import annotations

from pathlib import Path

import pytest

from marlctf.config import load_config, scenario_from_config


@pytest.fixture
def smoke_config_paths() -> dict[str, Path]:
    return {
        "match": Path("configs/smoke_match.yml"),
        "train": Path("configs/smoke_train.yml"),
        "evaluate": Path("configs/smoke_eval.yml"),
    }


@pytest.fixture
def smoke_match_config(smoke_config_paths: dict[str, Path]) -> dict:
    return load_config(smoke_config_paths["match"])


@pytest.fixture
def smoke_scenario(smoke_match_config: dict):
    return scenario_from_config(smoke_match_config)


@pytest.fixture
def sample_run_metadata(tmp_path: Path) -> dict:
    return {
        "run_id": "match-tiny-3v3-ctf-test",
        "run_type": "match",
        "config_path": "configs/smoke_match.yml",
        "scenario_id": "tiny-3v3-ctf",
        "seeds": [42],
        "policy_ids": ["red:scripted", "blue:scripted"],
        "artifact_dir": tmp_path.as_posix(),
    }
