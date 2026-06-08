#!/usr/bin/env python3
"""Health, login, and wake helper for the EVA/Kloe/Adam advisory trio."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Sequence


WORKSPACE_ROOT = Path(
    os.environ.get(
        "SMC_WORKSPACE_ROOT",
        "/Users/tuocheng/Library/CloudStorage/OneDrive-SuperMicroComputer,Inc",
    )
)
CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
ACTIVATION_FILE = CODEX_HOME / "agent-trio" / "activation.json"


@dataclass
class ProbeResult:
    agent: str
    role: str
    status: str
    command: str | None = None
    detail: str = ""
    login_attempted: bool = False
    login_status: str | None = None
    smoke_status: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def run_capture(
    cmd: Sequence[str],
    *,
    timeout: int,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(cmd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        env=dict(env or os.environ),
        check=False,
    )


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def resolve_executable(env_name: str, default_path: str, fallback_name: str) -> str | None:
    env_value = os.environ.get(env_name)
    candidates = [env_value, default_path, shutil.which(fallback_name)]
    for candidate in candidates:
        if candidate and Path(candidate).exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def summarize_failure(result: subprocess.CompletedProcess[str]) -> str:
    text = (result.stderr or result.stdout or "").strip().splitlines()
    if not text:
        return f"exit {result.returncode}"
    return text[-1][:300]


def login_and_recheck(
    result: ProbeResult,
    login_cmd: Sequence[str],
    check_cmd: Sequence[str],
    *,
    timeout: int,
    check_timeout: int,
) -> ProbeResult:
    result.login_attempted = True
    login = run_capture(login_cmd, timeout=timeout)
    if login.returncode != 0:
        result.login_status = f"failed: {summarize_failure(login)}"
        return result
    after = run_capture(check_cmd, timeout=check_timeout)
    if after.returncode == 0:
        result.status = "ok"
        result.detail = "authenticated after official login flow"
        result.login_status = "ok"
    else:
        result.login_status = f"login completed but check failed: {summarize_failure(after)}"
    return result


def probe_eva(login_if_needed: bool, login_timeout: int, check_timeout: int) -> ProbeResult:
    role = "Grok-backed decision optimizer and Codex routing mentor"
    grok = resolve_executable("GROK_BIN", "/Users/tuocheng/.grok/bin/grok", "grok")
    if not grok:
        return ProbeResult("EVA", role, "missing", detail="grok executable not found")

    check_cmd = [grok, "models"]
    check = run_capture(check_cmd, timeout=check_timeout)
    if check.returncode == 0:
        return ProbeResult("EVA", role, "ok", command=grok, detail="grok models succeeded")

    result = ProbeResult("EVA", role, "auth-needed", command=grok, detail=summarize_failure(check))
    if not login_if_needed:
        return result

    login_cmd = [grok, "login", "--oauth"] if is_interactive() else [grok, "login", "--device-auth"]
    return login_and_recheck(
        result,
        login_cmd,
        check_cmd,
        timeout=login_timeout,
        check_timeout=check_timeout,
    )


def smoke_eva(timeout: int) -> tuple[bool, str]:
    eva = resolve_executable("EVA_BIN", "/Users/tuocheng/.Grok/bin/eva", "eva")
    if not eva:
        return False, "eva wrapper not found"
    result = run_capture([eva, "--private", "Return exactly: EVA online"], timeout=timeout)
    if result.returncode == 0:
        return True, "eva wrapper returned successfully"
    return False, summarize_failure(result)


def probe_kloe(login_if_needed: bool, login_timeout: int, check_timeout: int) -> ProbeResult:
    role = "Antigravity-backed alternative-framing and evidence-gap reviewer"
    agy = resolve_executable("AGY_BIN", "/Users/tuocheng/.local/bin/agy", "agy")
    if not agy:
        return ProbeResult("Kloe", role, "missing", detail="agy executable not found")

    check_cmd = [agy, "models"]
    check = run_capture(check_cmd, timeout=check_timeout)
    if check.returncode == 0:
        return ProbeResult("Kloe", role, "ok", command=agy, detail="agy models succeeded")

    result = ProbeResult("Kloe", role, "auth-needed", command=agy, detail=summarize_failure(check))
    if not login_if_needed:
        return result
    if not is_interactive():
        result.login_attempted = False
        result.login_status = "blocked: run agy interactively to complete browser or manual URL auth"
        return result

    login_cmd = [
        agy,
        "--print-timeout",
        f"{max(login_timeout, 60)}s",
        "-p",
        "Return exactly: Antigravity authentication check",
    ]
    return login_and_recheck(
        result,
        login_cmd,
        check_cmd,
        timeout=login_timeout,
        check_timeout=check_timeout,
    )


def smoke_kloe(timeout: int) -> tuple[bool, str]:
    kloe = resolve_executable("KLOE_BIN", "/Users/tuocheng/.Antigravity/bin/kloe", "kloe")
    if not kloe:
        return False, "kloe wrapper not found"
    result = run_capture([kloe, "-p", "Return exactly: Kloe online"], timeout=timeout)
    if result.returncode == 0:
        return True, "kloe wrapper returned successfully"
    return False, summarize_failure(result)


def probe_adam(login_if_needed: bool, login_timeout: int, check_timeout: int) -> ProbeResult:
    role = "Claude-backed final auditor, token throttle, and handoff optimizer"
    claude = resolve_executable("CLAUDE_BIN", "/Users/tuocheng/.local/bin/claude", "claude")
    if not claude:
        return ProbeResult("Adam", role, "missing", detail="claude executable not found")

    check_cmd = [claude, "auth", "status"]
    check = run_capture(check_cmd, timeout=check_timeout)
    logged_in = check.returncode == 0 and '"loggedIn": true' in check.stdout
    if logged_in:
        return ProbeResult("Adam", role, "ok", command=claude, detail="claude auth status loggedIn=true")

    result = ProbeResult("Adam", role, "auth-needed", command=claude, detail=summarize_failure(check))
    if not login_if_needed:
        return result
    if not is_interactive():
        result.login_status = "blocked: run claude auth login --claudeai in an interactive terminal"
        return result

    return login_and_recheck(
        result,
        [claude, "auth", "login", "--claudeai"],
        check_cmd,
        timeout=login_timeout,
        check_timeout=check_timeout,
    )


def smoke_adam(timeout: int) -> tuple[bool, str]:
    adam = resolve_executable("ADAM_BIN", "/Users/tuocheng/.Claude/bin/adam", "adam")
    if not adam:
        return False, "adam wrapper not found"
    result = run_capture([adam, "--private", "Return exactly: Adam online"], timeout=timeout)
    if result.returncode == 0:
        return True, "adam wrapper returned successfully"
    return False, summarize_failure(result)


def collect_health(args: argparse.Namespace) -> list[ProbeResult]:
    probes = {
        "eva": probe_eva,
        "kloe": probe_kloe,
        "adam": probe_adam,
    }
    smokes = {
        "eva": smoke_eva,
        "kloe": smoke_kloe,
        "adam": smoke_adam,
    }
    selected = args.agent or ["eva", "kloe", "adam"]
    results = []
    for name in selected:
        result = probes[name](
            args.login_if_needed,
            args.login_timeout,
            args.check_timeout,
        )
        if args.smoke and result.ok:
            ok, detail = smokes[name](args.smoke_timeout)
            result.smoke_status = detail
            if not ok:
                result.status = "smoke-failed"
        results.append(result)
    return results


def print_health(results: Iterable[ProbeResult], *, as_json: bool) -> int:
    results = list(results)
    if as_json:
        print(json.dumps([asdict(r) for r in results], indent=2, sort_keys=True))
    else:
        for result in results:
            marker = "OK" if result.ok else "CHECK"
            print(f"{marker} {result.agent}: {result.status} - {result.detail}")
            if result.login_status:
                print(f"  login: {result.login_status}")
            if result.smoke_status:
                print(f"  smoke: {result.smoke_status}")
            if result.command:
                print(f"  command: {result.command}")
    return 0 if all(result.ok for result in results) else 1


def write_activation(enabled: bool, *, source: str) -> Path:
    ACTIVATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "enabled": enabled,
        "source": source,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "agents": {
            "eva": "Grok-backed decision optimizer and Codex routing mentor",
            "kloe": "Antigravity-backed alternative-framing reviewer",
            "adam": "Claude-backed final auditor and token governor",
        },
        "privacy_rule": "Use sanitized summaries for private/internal material unless raw sharing is explicitly approved.",
    }
    ACTIVATION_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return ACTIVATION_FILE


def command_wake(args: argparse.Namespace) -> int:
    if not args.yes:
        reply = input("Wake Adam, EVA, and Kloe for the next Codex tasks? Type ok to enable: ").strip().lower()
        if reply not in {"ok", "yes", "y"}:
            path = write_activation(False, source="agent_trio.py wake")
            print(f"Trio not enabled. Wrote {path}")
            return 0

    path = write_activation(True, source="agent_trio.py wake")
    print(f"Trio enabled. Wrote {path}")
    print("Use EVA for routing, Kloe for alternative critique, Adam for final audit/token discipline.")
    if args.health:
        results = collect_health(args)
        return print_health(results, as_json=args.json)
    return 0


def git_repos(root: Path, max_depth: int) -> Iterable[Path]:
    root = root.resolve()
    for git_dir in root.rglob(".git"):
        repo = git_dir.parent
        depth = len(repo.relative_to(root).parts)
        if depth <= max_depth:
            yield repo


def git_capture(repo: Path, *args: str) -> str:
    result = run_capture(["git", "-C", str(repo), *args], timeout=30)
    if result.returncode != 0:
        return f"ERROR: {summarize_failure(result)}"
    return result.stdout.strip()


def command_git_report(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    rows = []
    for repo in sorted(git_repos(root, args.max_depth)):
        rows.append(
            {
                "repo": str(repo),
                "branch": git_capture(repo, "branch", "--show-current"),
                "remote": git_capture(repo, "remote", "-v"),
                "status": git_capture(repo, "status", "--short", "--branch"),
            }
        )
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        for row in rows:
            print(f"\n## {row['repo']}")
            print(row["branch"])
            print(row["remote"])
            print(row["status"])
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON where supported.")
    sub = parser.add_subparsers(dest="command", required=True)

    health = sub.add_parser("health", help="Check EVA, Kloe, and Adam CLI/auth status.")
    health.add_argument("--json", action="store_true", help="Emit JSON.")
    health.add_argument("--agent", choices=["eva", "kloe", "adam"], action="append")
    health.add_argument("--login-if-needed", action="store_true")
    health.add_argument("--login-timeout", type=int, default=600)
    health.add_argument("--check-timeout", type=int, default=30)
    health.add_argument("--smoke", action="store_true", help="Run wrapper smoke prompts after auth checks.")
    health.add_argument("--smoke-timeout", type=int, default=180)
    health.set_defaults(func=lambda args: print_health(collect_health(args), as_json=args.json))

    wake = sub.add_parser("wake", help="Enable the trio for future Codex tasks.")
    wake.add_argument("--json", action="store_true", help="Emit JSON for health output.")
    wake.add_argument("--yes", action="store_true", help="Enable without prompting.")
    wake.add_argument("--health", action="store_true", help="Run health after enabling.")
    wake.add_argument("--agent", choices=["eva", "kloe", "adam"], action="append")
    wake.add_argument("--login-if-needed", action="store_true")
    wake.add_argument("--login-timeout", type=int, default=600)
    wake.add_argument("--check-timeout", type=int, default=30)
    wake.add_argument("--smoke", action="store_true", help="Run wrapper smoke prompts after auth checks.")
    wake.add_argument("--smoke-timeout", type=int, default=180)
    wake.set_defaults(func=command_wake)

    report = sub.add_parser("git-report", help="List nearby git repos, remotes, branches, and dirty status.")
    report.add_argument("--json", action="store_true", help="Emit JSON.")
    report.add_argument("--root", default=str(WORKSPACE_ROOT))
    report.add_argument("--max-depth", type=int, default=3)
    report.set_defaults(func=command_git_report)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
