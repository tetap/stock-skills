# 发布前检查（Windows）：单元测试 + MCP parity
param(
    [switch]$SkipParity
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
    Write-Error "未找到 .venv，请先运行: powershell -ExecutionPolicy Bypass -File scripts/install.ps1"
}

Write-Host "[check] 单元测试..."
& $Py -m unittest discover -s tests -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $SkipParity) {
    Write-Host "[check] MCP 工具 parity..."
    & $Py -m unittest tests.test_mcp_parity -v
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "[check] 全部通过"
