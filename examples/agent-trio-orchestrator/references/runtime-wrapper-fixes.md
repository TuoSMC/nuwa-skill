# Runtime Wrapper Fixes

The local Adam wrapper was hardened while creating this skill.

Key shell lessons:

- Do not place the prompt after Claude Code variadic options such as `--tools` or `--add-dir`; use `--tools=Read,Grep,Glob,LS` and `--add-dir=/path` forms.
- Do not pipe a long skill index into `head` while `set -o pipefail` is active. When `head` exits early, upstream commands can receive SIGPIPE and make the whole wrapper exit `141`.
- Prefer an awk limiter that reads the full stream:

```bash
awk -v limit="$limit" '!seen[$0]++ { if (count < limit) print; count++ }'
```

Verification used:

```bash
bash -n /Users/tuocheng/.Claude/bin/adam
/Users/tuocheng/.Claude/bin/adam --private "Return exactly: Adam online"
python3 /Users/tuocheng/.codex/skills/agent-trio-orchestrator/scripts/agent_trio.py health --agent adam --smoke --json
```
