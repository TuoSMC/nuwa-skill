<# 
Installs or verifies the Windows tooling needed for the EVA/Kloe/Adam trio.

Official installers used:
- Antigravity CLI: https://antigravity.google/docs/cli-install
- Grok Build CLI: https://x.ai/cli
- Claude Code: https://docs.anthropic.com/en/docs/claude-code/getting-started

This script does not store passwords, tokens, cookies, SSH keys, or API keys.
#>

[CmdletBinding()]
param(
    [string]$GitRepo = "",
    [switch]$Login,
    [switch]$PushReport,
    [switch]$SkipWingetPackages
)

$ErrorActionPreference = "Stop"
$Report = New-Object System.Collections.Generic.List[string]

function Add-Report {
    param([string]$Line)
    $timestamp = (Get-Date).ToUniversalTime().ToString("s") + "Z"
    $Report.Add("- [$timestamp] $Line")
    Write-Host $Line
}

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-Logged {
    param(
        [string]$Label,
        [scriptblock]$Block
    )
    try {
        & $Block
        Add-Report "${Label}: OK"
    }
    catch {
        Add-Report "${Label}: FAILED - $($_.Exception.Message)"
        throw
    }
}

function Ensure-WingetPackage {
    param(
        [string]$CommandName,
        [string]$PackageId,
        [string]$Label
    )
    if (Test-Command $CommandName) {
        Add-Report "$Label already available: $CommandName"
        return
    }
    if ($SkipWingetPackages) {
        Add-Report "$Label missing and winget install skipped"
        return
    }
    if (-not (Test-Command winget)) {
        Add-Report "winget missing; install $Label manually or rerun after App Installer is available"
        return
    }
    Invoke-Logged "Install $Label via winget" {
        winget install --id $PackageId --accept-package-agreements --accept-source-agreements --silent
    }
}

function Add-UserPath {
    param([string]$PathToAdd)
    if (-not (Test-Path $PathToAdd)) {
        return
    }
    $current = [Environment]::GetEnvironmentVariable("Path", "User")
    $parts = @()
    if ($current) {
        $parts = $current -split ";"
    }
    if ($parts -notcontains $PathToAdd) {
        [Environment]::SetEnvironmentVariable("Path", (($parts + $PathToAdd) -join ";"), "User")
        $env:Path = "$env:Path;$PathToAdd"
        Add-Report "Added to user PATH: $PathToAdd"
    }
}

Invoke-Logged "Enable TLS 1.2" {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
}

Ensure-WingetPackage -CommandName git -PackageId Git.Git -Label "Git for Windows"
Ensure-WingetPackage -CommandName gh -PackageId GitHub.cli -Label "GitHub CLI"
Ensure-WingetPackage -CommandName node -PackageId OpenJS.NodeJS.LTS -Label "Node.js LTS"

if (Test-Command npm) {
    $npmPrefix = Join-Path $env:USERPROFILE ".npm-global"
    New-Item -ItemType Directory -Force -Path $npmPrefix | Out-Null
    npm config set prefix $npmPrefix | Out-Null
    Add-UserPath (Join-Path $npmPrefix "bin")
    Invoke-Logged "Install or update Claude Code" {
        npm install -g @anthropic-ai/claude-code
    }
}
else {
    Add-Report "npm missing; Claude Code install skipped"
}

$gitBash = "C:\Program Files\Git\bin\bash.exe"
if (Test-Path $gitBash) {
    [Environment]::SetEnvironmentVariable("CLAUDE_CODE_GIT_BASH_PATH", $gitBash, "User")
    $env:CLAUDE_CODE_GIT_BASH_PATH = $gitBash
    Add-Report "Set CLAUDE_CODE_GIT_BASH_PATH"
}

Invoke-Logged "Install or update Grok Build CLI" {
    irm https://x.ai/cli/install.ps1 | iex
}
Add-UserPath (Join-Path $env:USERPROFILE ".grok\bin")

Invoke-Logged "Install or update Antigravity CLI" {
    irm https://antigravity.google/cli/install.ps1 | iex
}
Add-UserPath (Join-Path $env:LOCALAPPDATA "agy\bin")

if (Test-Command grok) {
    Invoke-Logged "Verify grok" { grok --version }
    if ($Login) {
        Invoke-Logged "Grok login" { grok login --oauth }
    }
}
else {
    Add-Report "grok still not found after installer; open a new terminal or check user PATH"
}

if (Test-Command agy) {
    Invoke-Logged "Verify agy" { agy --help | Out-Null }
    if ($Login) {
        Add-Report "Antigravity login check may open a browser or print a manual URL"
        Invoke-Logged "Antigravity auth probe" { agy models }
    }
}
else {
    Add-Report "agy still not found after installer; open a new terminal or check user PATH"
}

if (Test-Command claude) {
    Invoke-Logged "Verify claude" { claude --version }
    if ($Login) {
        Invoke-Logged "Claude auth status or login" {
            $status = claude auth status
            if ($LASTEXITCODE -ne 0 -or ($status -notmatch '"loggedIn": true')) {
                claude auth login --claudeai
            }
        }
    }
}
else {
    Add-Report "claude still not found after npm install; open a new terminal or check npm user prefix PATH"
}

if (Test-Command gh) {
    if ($Login) {
        Invoke-Logged "GitHub auth status or login" {
            gh auth status
            if ($LASTEXITCODE -ne 0) {
                gh auth login -w
            }
        }
    }
}
else {
    Add-Report "gh missing; GitHub report push unavailable"
}

$reportName = "agent-trio-windows-bootstrap-{0}.md" -f (Get-Date -Format "yyyyMMdd-HHmmss")
$reportDir = if ($GitRepo) { Join-Path $GitRepo "agent-trio" } else { Join-Path $env:USERPROFILE ".agent-trio" }
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$reportPath = Join-Path $reportDir $reportName

$header = @(
    "# Agent Trio Windows Bootstrap Report",
    "",
    "- Machine: $env:COMPUTERNAME",
    "- User: $env:USERNAME",
    "- Created: $((Get-Date).ToUniversalTime().ToString("s"))Z",
    "- Secrets included: no",
    ""
)
($header + $Report) | Set-Content -Encoding UTF8 -Path $reportPath
Add-Report "Wrote report: $reportPath"

if ($PushReport) {
    if (-not $GitRepo) {
        throw "Use -GitRepo <path> with -PushReport"
    }
    if (-not (Test-Path (Join-Path $GitRepo ".git"))) {
        throw "GitRepo is not a git checkout: $GitRepo"
    }
    if (-not (Test-Command git)) {
        throw "git command not available"
    }
    Push-Location $GitRepo
    try {
        $relativeReportPath = "agent-trio/$reportName"
        git add -- $relativeReportPath
        git commit -m "chore: add agent trio Windows bootstrap report"
        git push
        Add-Report "Pushed report to GitHub"
    }
    finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "Done. Report: $reportPath"
