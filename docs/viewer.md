# Replay Viewer

Run a deterministic smoke match and write replay artifacts:

```powershell
marlctf match --config configs/smoke_match.yml --seed 42 --artifact-dir artifacts/viewer-match
```

The match artifact directory contains:

```text
run.json
metrics.jsonl
events.jsonl
replay.jsonl
```

Open the local viewer for that run:

```powershell
marlctf viewer --artifact artifacts/viewer-match
```

Use `--no-open` to start the local server without launching a browser:

```powershell
marlctf viewer --artifact artifacts/viewer-match --host 127.0.0.1 --port 8000 --no-open
```

`run.json` records `replay_available: true` and `replay_paths` when replay
snapshots are present. Older artifact directories without replay files remain
valid for later metrics and comparison views.
