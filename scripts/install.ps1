# PowerShell 安装脚本（Windows）
# 用法: powershell -ExecutionPolicy Bypass -File scripts/install.ps1
param(
    [string]$Target = "cursor",
    [ValidateSet("user", "project")]
    [string]$Scope = "user",
    [switch]$SkipDeps,
    [switch]$WithMl,
    [switch]$Copy,
    [switch]$Unlink
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SkillsSrc = Join-Path $Root "agent-skills"
$CommandsSrc = Join-Path $Root "agent-commands"
$SlashSrc = Join-Path $Root "agent-slash-skills"
$Venv = Join-Path $Root ".venv"
$Py = Join-Path $Venv "Scripts\python.exe"
$Pip = Join-Path $Venv "Scripts\pip.exe"

function Get-SkillsDest([string]$Agent) {
    if ($Scope -eq "project") {
        switch ($Agent) {
            "cursor" { return Join-Path $Root ".cursor\skills" }
            "claude" { return Join-Path $Root ".claude\skills" }
            "codex"  { return Join-Path $Root ".codex\skills" }
            "agents" { return Join-Path $Root ".agents\skills" }
        }
    } else {
        switch ($Agent) {
            "cursor" { return Join-Path $env:USERPROFILE ".cursor\skills" }
            "claude" { return Join-Path $env:USERPROFILE ".claude\skills" }
            "codex"  { return Join-Path $env:USERPROFILE ".codex\skills" }
            "agents" { return Join-Path $env:USERPROFILE ".agents\skills" }
        }
    }
    throw "未知 target: $Agent"
}

function Sync-McpJson {
    $McpDir = Join-Path $Root ".cursor"
    $McpPath = Join-Path $McpDir "mcp.json"
    if (-not (Test-Path $Py)) { return }
    New-Item -ItemType Directory -Force -Path $McpDir | Out-Null
    $data = @{ mcpServers = @{} }
    if (Test-Path $McpPath) {
        $data = Get-Content $McpPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
        if (-not $data.mcpServers) { $data.mcpServers = @{} }
    }
    $data.mcpServers["eastmoney-stock"] = @{
        command = $Py
        args = @("-m", "mcp_server")
        cwd = $Root
    }
    ($data | ConvertTo-Json -Depth 6) + "`n" | Set-Content -Path $McpPath -Encoding UTF8
    Write-Host "[mcp] 已同步 $McpPath"
}

function Install-Entry([string]$Src, [string]$Dest, [string[]]$SkipNames, [switch]$RequireSkill) {
    New-Item -ItemType Directory -Force -Path $Dest | Out-Null
    Get-ChildItem $Src | ForEach-Object {
        $name = $_.Name
        $base = $name -replace '\.md$',''
        if ($SkipNames -contains $name -or $SkipNames -contains $base) { return }
        if ($RequireSkill -and -not (Test-Path (Join-Path $_.FullName "SKILL.md"))) { return }
        $target = Join-Path $Dest $name
        if ($Unlink) {
            if (Test-Path $target) { Remove-Item -Recurse -Force $target; Write-Host "removed $target" }
            return
        }
        if (Test-Path $target) { Remove-Item -Recurse -Force $target }
        if ($Copy) {
            Copy-Item -Recurse $_.FullName $target
            Write-Host "copied $target"
        } else {
            cmd /c mklink /J `"$target`" `"$($_.FullName)`" 2>$null
            if (-not (Test-Path $target)) {
                Copy-Item -Recurse $_.FullName $target
                Write-Host "copied (no symlink) $target"
            } else {
                Write-Host "linked $target"
            }
        }
    }
}

$Skip = @("stock-investment-advisor", "stock-role")
$Targets = if ($Target -eq "all") { @("cursor","claude","codex","agents") } else { @($Target) }

if (-not $SkipDeps -and -not $Unlink) {
    $SystemPy = Get-Command python -ErrorAction SilentlyContinue
    if (-not $SystemPy) { throw "未找到 python，请先安装 Python 3.12+" }
    if (-not (Test-Path $Py)) {
        Write-Host "[python] 创建虚拟环境: $Venv"
        & $SystemPy.Source -m venv $Venv
    }
    $LockFile = Join-Path $Root "requirements.lock"
    $ReqFile = if (Test-Path $LockFile) { $LockFile } else { Join-Path $Root "requirements.txt" }
    Write-Host "[python] pip install -r $ReqFile"
    & $Pip install -q --upgrade pip wheel
    & $Pip install -q -r $ReqFile
    if ($WithMl) {
        & $Pip install -q -r (Join-Path $Root "requirements-ml.txt")
    }
    & $Py -c "import mcp; print('[python] mcp OK')"
}

if ($Target -match "cursor" -or $Target -eq "all") {
    Sync-McpJson
}

foreach ($agent in $Targets) {
    $dest = Get-SkillsDest $agent
    Write-Host "[$agent skills] -> $dest"
    Install-Entry $SkillsSrc $dest $Skip -RequireSkill
    if ($agent -eq "cursor") {
        $cmdDest = if ($Scope -eq "project") { Join-Path $Root ".cursor\commands" } else { Join-Path $env:USERPROFILE ".cursor\commands" }
        Install-Entry $CommandsSrc $cmdDest @("stock-role.md","stock-role")
    } elseif ($agent -ne "cursor") {
        Install-Entry $SlashSrc $dest $Skip -RequireSkill
    }
}

Write-Host "安装完成。Python: $Py"
Write-Host "重启 Cursor 使 MCP / Skills 生效。"
