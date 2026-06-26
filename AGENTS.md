# MARLCTF Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-06-26

## Active Technologies
- Python 3.11+ for artifact generation and CLI integration; browser-standard HTML/CSS/JavaScript for the local viewer + Existing MARLCTF package dependencies; no required frontend build dependency for the first viewer (002-replay-viewer)
- Local filesystem JSON/JSONL artifacts under run artifact directories (002-replay-viewer)

- Python 3.11+ + PettingZoo, Gymnasium, NumPy, PyTorch, PyYAML or TOML config parsing, pytest (001-marl-ctf-sim)

## Project Structure

```text
src/
tests/
configs/
artifacts/
```

## Commands

pytest
pytest tests/contract tests/unit

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 002-replay-viewer: Added Python 3.11+ for artifact generation and CLI integration; browser-standard HTML/CSS/JavaScript for the local viewer + Existing MARLCTF package dependencies; no required frontend build dependency for the first viewer

- 001-marl-ctf-sim: Added Python 3.11+ + PettingZoo, Gymnasium, NumPy, PyTorch, PyYAML or TOML config parsing, pytest

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
