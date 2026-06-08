---
name: workflow-packaging-review
description: |
  Evidence-first review for turning repeated manual work into the smallest useful skill, custom subagent, automation, or settings update.
  Use when the user asks Codex to look across recent sessions, memories, rollout summaries, Chronicle/activity logs, existing skills, agents, or automations to improve future collaboration, package repeated workflows, create reusable playbooks, or decide what should not be packaged.
  Triggers include "look across my sessions", "identify repeated workflows", "make our collaboration better", "turn this into a skill/agent/automation", "put this into future settings", and similar requests.
---

# Workflow Packaging Review

## Overview

Distill collaboration patterns the way Nuwa distills people: extract the repeatable operating system, keep the evidence trail visible, and only create assets that will actually save work next time.

This is not a brainstorming skill. It is a narrow audit-and-packaging workflow with a clear stop condition: a compact shortlist, high-confidence missing assets created or extended, and explicit skips.

## Evidence Order

Use available evidence in this order:

1. Recent Codex sessions and task summaries.
2. Codex Memories and rollout summaries.
3. Chronicle or other activity logs, if enabled. Use them for discovery only; confirm important details in the source system when possible.
4. Existing skills, custom agents, automations, AGENTS.md files, and repo-specific conventions.

If a source is unavailable, say so briefly and continue with the remaining sources. Do not invent activity history.

## Workflow

### 1. Set the Review Window

Default to the last 30 days. If less history exists, use all available history and state the shorter window.

### 2. Inventory Existing Reusable Assets

Before recommending anything new, look for:

- Global and workspace `AGENTS.md`.
- Skills in the active runtime and relevant repos.
- Installed UI/UX and frontend design skills, especially `ui-ux-pro-max`, when the repeated workflow concerns interface design, dashboards, landing pages, components, accessibility, charts, color, typography, or interaction quality.
- Installed software-development process skills, especially Superpowers, when the repeated workflow concerns brainstorming, planning, TDD, debugging, verification, code review, worktrees, branch finishing, or parallel/subagent execution.
- Installed reach/research skills, especially `agent-reach`, when the repeated workflow concerns internet search, URL reading, platform/social discovery, GitHub exploration, RSS, or video/subtitle extraction.
- Memory skills and ad-hoc memory notes.
- Custom subagents or agent definitions.
- Automations or recurring jobs.

Prefer extending an adequate existing asset over creating a parallel one.

### 3. Build a Compact Shortlist

For each candidate, include:

- Repeated workflow.
- Supporting evidence and dates.
- Frequency and confidence.
- Recommended form: `skill`, `subagent`, `automation`, `extend existing`, or `skip`.
- Why it is or is not worth creating.

Keep the shortlist compact. Group near-duplicates.

### 4. Apply the Creation Gate

Only act on a candidate when all of these are true:

- It occurred at least twice, or is clearly likely to recur and costly to repeat.
- It has stable inputs, a repeatable procedure, and a clear output or stopping condition.
- It would materially improve speed, quality, consistency, or reliability.
- It is not already adequately covered.

Skip candidates that are one-off, ambiguous, sensitive, poorly evidenced, or better handled by normal reasoning.

### 5. Choose the Smallest Form

- `skill`: Use for a reusable workflow or playbook with stable steps. Follow the active skill-creation rules and validate the skill.
- `subagent`: Use only for a bounded specialist role or investigation task that can be delegated independently. If no subagent mechanism is available, recommend it but do not fake one.
- `automation`: Use for scheduled or recurring checks, reports, reminders, or monitors. Inspect existing automations first and use the automation tool when available.
- `extend existing`: Use when a current skill, AGENTS.md, memory note, or automation is close enough.
- `skip`: Use when packaging would add clutter or false certainty.

### 6. Create Only High-Confidence Missing Items

Keep created assets narrow and source-aware. Avoid broad "collaboration OS" assets unless the evidence proves multiple recurring workflows share the same core procedure.

If the candidate is UI/UX or frontend-facing, first consult the installed `ui-ux-pro-max` skill and treat it as the default design reasoning source. Package only the project-specific workflow around it, such as validation steps, repo conventions, or product-specific design rules, instead of copying its general design database.

If the candidate is a software-development process, first consult the installed Superpowers skills. Package only the project-specific constraints, handoffs, or validation evidence that Superpowers does not already cover.

If the candidate is research or internet-reach related, first consult `agent-reach` and any available first-party connectors. Package only the routing, source priorities, credential boundaries, and output expectations that recur for this workspace.

When creating a skill:

- Put trigger language in the `description`, not only the body.
- Include inputs, procedure, validation, and stop conditions.
- Keep the body lean; use references only when details are too large for the main file.
- Validate with the runtime's skill validation script if available.

When updating settings:

- Prefer `AGENTS.md` for collaboration rules.
- Avoid changing sensitive global config unless the user explicitly asked for that exact change.
- If both global and workspace settings exist, make the workspace file specific and avoid duplicating the global file verbatim.

## Output Format

Return the shortlist first, then the action summary.

Use this structure:

```text
Shortlist
- Workflow:
  Evidence:
  Frequency/confidence:
  Recommended form:
  Decision:

Created or Extended
- ...

Skipped
- ...

Needs More Evidence
- ...
```

If no high-confidence missing items exist, say that clearly and do not create anything.
