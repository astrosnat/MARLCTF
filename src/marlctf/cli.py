"""Command line interface for MARLCTF."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from marlctf.config import ConfigError
from marlctf.evaluation.evaluator import run_evaluation
from marlctf.runner import run_match
from marlctf.training.runner import run_training
from marlctf.viewer.server import run_viewer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="marlctf")
    subparsers = parser.add_subparsers(dest="command", required=True)

    match = subparsers.add_parser("match", help="Run one 3v3 CTF match")
    match.add_argument("--config", required=True)
    match.add_argument("--seed", type=int)
    match.add_argument("--policy-red")
    match.add_argument("--policy-blue")
    match.add_argument("--artifact-dir")
    match.add_argument("--render", choices=["none", "ansi", "human"], default="none")
    train = subparsers.add_parser("train", help="Run a bounded local VDN training smoke run")
    train.add_argument("--config", required=True)
    train.add_argument("--seed", type=int)
    train.add_argument("--artifact-dir")
    train.add_argument("--checkpoint-every", type=int)
    train.add_argument("--episodes", type=int)
    evaluate = subparsers.add_parser("evaluate", help="Compare policies over fixed seeds")
    evaluate.add_argument("--config", required=True)
    evaluate.add_argument("--artifact-dir")
    evaluate.add_argument("--candidate")
    evaluate.add_argument("--baseline")
    viewer = subparsers.add_parser("viewer", help="Open the local replay and metrics viewer")
    viewer.add_argument("--artifact")
    viewer.add_argument("--host", default="127.0.0.1")
    viewer.add_argument("--port", type=int, default=8000)
    viewer.add_argument("--no-open", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "match":
        try:
            run_match(
                Path(args.config),
                seed=args.seed,
                artifact_dir=args.artifact_dir,
                policy_red=args.policy_red,
                policy_blue=args.policy_blue,
                render=args.render,
            )
            return 0
        except ConfigError as exc:
            print(f"config error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"runtime error: {exc}", file=sys.stderr)
            return 2
    if args.command == "train":
        try:
            run_training(
                Path(args.config),
                seed=args.seed,
                artifact_dir=args.artifact_dir,
                episodes=args.episodes,
            )
            return 0
        except ConfigError as exc:
            print(f"config error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"runtime error: {exc}", file=sys.stderr)
            return 2
    if args.command == "evaluate":
        try:
            run_evaluation(
                Path(args.config),
                artifact_dir=args.artifact_dir,
                candidate=args.candidate,
                baseline=args.baseline,
            )
            return 0
        except ConfigError as exc:
            print(f"config error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"runtime error: {exc}", file=sys.stderr)
            return 2
    if args.command == "viewer":
        artifact = Path(args.artifact) if args.artifact else None
        if artifact is not None and not artifact.exists():
            print(f"artifact path does not exist: {artifact}", file=sys.stderr)
            return 1
        try:
            return run_viewer(
                artifact=artifact,
                host=args.host,
                port=args.port,
                open_browser=not args.no_open,
            )
        except OSError as exc:
            print(f"viewer error: {exc}", file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"runtime error: {exc}", file=sys.stderr)
            return 2
    parser.error(f"unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
