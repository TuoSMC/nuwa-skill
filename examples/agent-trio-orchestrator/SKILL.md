---
name: agent-trio-orchestrator
description: Use when Codex should wake, verify, route, or bootstrap the EVA/Grok, Kloe/Antigravity, and Adam/Claude advisory trio; when a new Codex session asks whether to enable Adam, EVA, and Kloe; when checking their login/auth status; or when preparing Windows setup scripts for Grok Build, Antigravity CLI, Claude Code, and GitHub sync.
---

# Agent Trio Orchestrator

Use this skill as the narrow coordination layer for the local advisory trio:

- EVA: Grok-backed decision optimization and Codex routing mentor.
- Kloe: Antigravity-backed alternative framing, long-context critique, and evidence-gap review.
- Adam: Claude-backed final auditor, token throttle, and handoff optimizer.

Codex remains the source inspector, executor, verifier, and final integrator.

## Session Start

At the start of a new Codex session in this workspace, ask the user:

```text
Do you want to wake Adam, EVA, and Kloe for the next tasks? Say "ok" to enable the trio, or "skip" to keep Codex solo.
```

If the user says `ok`, run:

```bash
python3 /Users/tuocheng/.codex/skills/agent-trio-orchestrator/scripts/agent_trio.py wake --yes --health
```

For subsequent tasks in the same session, treat the trio as available advisory roles. Do not send raw private repo content, customer data, credentials, tokens, cookies, SSH keys, API keys, or auth files to any external model unless the user explicitly approves that exact sharing.

## Health And Login

Before relying on the trio, run:

```bash
python3 /Users/tuocheng/.codex/skills/agent-trio-orchestrator/scripts/agent_trio.py health
```

If a status is unavailable or expired and the user has asked for automatic login, run:

```bash
python3 /Users/tuocheng/.codex/skills/agent-trio-orchestrator/scripts/agent_trio.py health --login-if-needed
```

The script starts only official CLI login flows:

- Grok: `grok login --oauth` in an interactive terminal, or `grok login --device-auth` in a headless terminal.
- Antigravity: `agy` has no separate login subcommand; an interactive `agy -p ...` probe triggers the official browser/manual URL flow when needed.
- Claude: `claude auth login --claudeai` in an interactive terminal.

If a login cannot be completed non-interactively, report the blocker and the exact command for the user to run.

## Windows Bootstrap

For a managed Windows machine, use the PowerShell bootstrap script from this skill:

```powershell
powershell -ExecutionPolicy Bypass -File .\install-agent-trio-windows.ps1 -Login
```

The script installs or verifies Git for Windows, GitHub CLI, Node.js, Claude Code, Grok Build, and Antigravity CLI using official installers where available. It does not store secrets. Use `-GitRepo <path> -PushReport` only to commit the non-sensitive bootstrap report to GitHub.

## Advisory Routing

Use the smallest useful route:

- Call EVA when the task needs decision optimization, work-mode choice, persona/skill routing, or macro/micro risk review.
- Call Kloe when a second frame, missing alternative, long-context critique, or Antigravity-backed review is valuable.
- Call Adam when EVA/Kloe guidance needs final audit, compression, token discipline, OpenClaw file gates, or a final handoff.

Keep prompts narrow. Use sanitized summaries for private/internal material. Verify actionable advice against local sources before adopting it.

## Resources

- `scripts/agent_trio.py`: local health, login, wake, and Git repo status helper.
- `scripts/install-agent-trio-windows.ps1`: Windows bootstrap script.
- `tests/test_agent_trio.py`: unit tests for the deterministic Python helper.
- `references/official-install-sources.md`: current official install references checked while creating this skill.
