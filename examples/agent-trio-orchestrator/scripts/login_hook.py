#!/usr/bin/env python3
"""Small wrapper for Adam/EVA/Kloe login, health, wake, and smoke checks."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


DEFAULT_AGENT_TRIO = Path(__file__).with_name("agent_trio.py")


def agent_trio_script() -> Path:
    return Path(os.environ.get("AGENT_TRIO_SCRIPT", str(DEFAULT_AGENT_TRIO))).expanduser()


def run_agent_trio(args: Sequence[str]) -> int:
    script = agent_trio_script()
    if not script.exists():
        print(f"agent-trio helper not found: {script}", file=sys.stderr)
        return 2

    cmd = [sys.executable, str(script), *args]
    return subprocess.call(cmd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run official CLI-backed login and health checks for Adam, EVA, and Kloe."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["health", "login", "wake", "smoke"],
        default="health",
        help=(
            "health checks current auth; login checks auth and starts official login flows "
            "when possible; wake enables the trio and checks auth; smoke runs bounded wrapper prompts."
        ),
    )
    parser.add_argument("--json", action="store_true", help="Forward JSON output where supported.")
    parser.add_argument("--agent", choices=["eva", "kloe", "adam"], action="append")
    parser.add_argument("--login-timeout", type=int, default=600)
    parser.add_argument("--check-timeout", type=int, default=30)
    parser.add_argument("--smoke-timeout", type=int, default=180)
    return parser


def forwarded_args(args: argparse.Namespace) -> list[str]:
    base: list[str]
    if args.mode == "wake":
        base = [
            "wake",
            "--yes",
            "--health",
            "--login-if-needed",
        ]
    else:
        base = ["health"]
        if args.mode in {"login", "smoke"}:
            base.append("--login-if-needed")
        if args.mode == "smoke":
            base.append("--smoke")

    if args.json:
        base.append("--json")
    for agent in args.agent or []:
        base.extend(["--agent", agent])
    base.extend(["--login-timeout", str(args.login_timeout)])
    base.extend(["--check-timeout", str(args.check_timeout)])
    if args.mode == "smoke":
        base.extend(["--smoke-timeout", str(args.smoke_timeout)])
    return base


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_agent_trio(forwarded_args(args))


if __name__ == "__main__":
    raise SystemExit(main())
