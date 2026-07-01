#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/python ]]; then
  echo "[test] 未找到 .venv，运行 install.sh 创建环境..."
  bash "$ROOT/scripts/install.sh" --target cursor --scope project --what skills --skip-deps
  if [[ ! -x .venv/bin/python ]]; then
    py="$(command -v python3 || command -v python)"
    "$py" -m venv .venv
  fi
  .venv/bin/pip install -q --upgrade pip wheel
  .venv/bin/pip install -q -r requirements.txt
fi

source .venv/bin/activate
python -m unittest discover -s tests -p 'test_*.py' -v
