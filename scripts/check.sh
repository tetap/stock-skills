#!/usr/bin/env bash
# 发布前检查：单元测试 + MCP 工具 parity
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[check] 单元测试..."
bash scripts/test.sh

echo "[check] MCP 工具 parity..."
source .venv/bin/activate
python -m unittest tests.test_mcp_parity -v

echo "[check] 全部通过"
