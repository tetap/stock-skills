#!/usr/bin/env bash
# 只读冒烟：调用真实东方财富接口（需网络，非 CI 默认）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/python ]]; then
  echo "[smoke] 未找到 .venv，请先 bash scripts/install.sh" >&2
  exit 1
fi

export LIVE=1
echo "[smoke] LIVE=1 运行只读接口测试..."
.venv/bin/python -m unittest tests.test_live_smoke -v
