# Official Install Sources

Checked on 2026-06-07 in the local timezone.

Use these as source-aware anchors when updating the Windows bootstrap script:

- Antigravity CLI install docs: https://antigravity.google/docs/cli-install
  - Windows PowerShell installer: `irm https://antigravity.google/cli/install.ps1 | iex`
  - Windows install path: `%LOCALAPPDATA%\agy\bin`
  - Auth uses the operating system keyring or browser/manual URL flow.
- Grok Build CLI docs/product page: https://x.ai/cli and local Grok docs under `/Users/tuocheng/.Grok/docs/user-guide/`
  - Windows PowerShell installer: `irm https://x.ai/cli/install.ps1 | iex`
  - Login commands: `grok login --oauth` or `grok login --device-auth`
- Claude Code setup docs: https://docs.anthropic.com/en/docs/claude-code/getting-started
  - Standard install: `npm install -g @anthropic-ai/claude-code`
  - Windows support: WSL or Git for Windows; Node.js 18+ required.
- GitHub CLI install docs: https://cli.github.com/
  - Common Windows package id: `GitHub.cli`

Do not add API keys, auth files, cookies, SSH keys, or tokens to this skill or its reports.
