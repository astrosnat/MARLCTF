# MARLCTF

Toy 3v3 capture-the-flag multi-agent reinforcement learning simulation.

MARLCTF provides a small PettingZoo-style Parallel environment, deterministic scripted and random baselines, a CPU-friendly VDN smoke trainer, and fixed-seed evaluation artifacts for comparing candidate policies.

## Install

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

After installation, use the console command:

```powershell
marlctf --help
```

When running directly from the source tree without installing, set `PYTHONPATH` first:

```powershell
$env:PYTHONPATH = "src"
python -m marlctf.cli --help
```

## Run A Match

```powershell
marlctf match --config configs/smoke_match.yml --seed 42 --artifact-dir artifacts/smoke-match
```

Source-tree equivalent:

```powershell
$env:PYTHONPATH = "src"
python -m marlctf.cli match --config configs/smoke_match.yml --seed 42 --artifact-dir artifacts/smoke-match
```

Outputs:

```text
artifacts/smoke-match/run.json
artifacts/smoke-match/metrics.jsonl
artifacts/smoke-match/events.jsonl
```

## Train VDN

```powershell
marlctf train --config configs/smoke_train.yml --seed 7 --artifact-dir artifacts/smoke-train
```

For a shorter smoke run:

```powershell
$env:PYTHONPATH = "src"
python -m marlctf.cli train --config configs/smoke_train.yml --seed 7 --artifact-dir artifacts/smoke-train --episodes 3
```

Outputs:

```text
artifacts/smoke-train/run.json
artifacts/smoke-train/metrics.jsonl
artifacts/smoke-train/checkpoints/latest.pt
```

## Evaluate Policies

```powershell
marlctf evaluate --config configs/smoke_eval.yml --artifact-dir artifacts/smoke-eval
```

The smoke evaluation compares the configured candidate policy against the baseline over 10 fixed seeds. Policy types can be overridden:

```powershell
marlctf evaluate --config configs/smoke_eval.yml --artifact-dir artifacts/eval-random --candidate random --baseline scripted
```

Outputs:

```text
artifacts/smoke-eval/run.json
artifacts/smoke-eval/metrics.jsonl
artifacts/smoke-eval/comparison.json
```

## Inspect Artifacts

PowerShell examples:

```powershell
Get-Content artifacts/smoke-match/run.json
Get-Content artifacts/smoke-match/metrics.jsonl -TotalCount 3
Get-Content artifacts/smoke-eval/comparison.json
```

Validation summaries from Phase 6 are written under:

```text
artifacts/validation/rule_validity_summary.json
artifacts/validation/quickstart_summary.json
artifacts/validation/test_summary.json
```

## Documentation

- [Default scenario and observation contract](docs/scenario.md)
- [Artifact schemas and examples](docs/artifacts.md)
