# 发布前检查（Windows）：单元测试 + MCP parity
param(
    [switch]$SkipParity
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$Py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
    Write-Error "未找到 .venv，请先运行: powershell -ExecutionPolicy Bypass -File scripts/install.ps1"
}

Write-Host "[check] 单元测试..."
$failed = @()
Get-ChildItem (Join-Path $Root "tests\test_*.py") | ForEach-Object {
    $mod = "tests." + $_.BaseName
    Write-Host "  -> $mod"
    & $Py -m unittest $mod -v
    if ($LASTEXITCODE -ne 0) {
        $failed += $mod
    }
}
if ($failed.Count -gt 0) {
    Write-Error ("单元测试失败: " + ($failed -join ", "))
    exit 1
}

if (-not $SkipParity) {
    Write-Host "[check] MCP 工具 parity..."
    & $Py -m unittest tests.test_mcp_parity -v
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

Write-Host "[check] 全部通过"
