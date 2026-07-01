#!/usr/bin/env bash
# 训练演示用 Alpha158 LightGBM（调优超参 + embargo，约 2~5 分钟）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/python ]]; then
  echo "[demo] 创建 .venv..."
  bash "$ROOT/scripts/install.sh" --target cursor --scope project --what skills --skip-deps
fi

if ! .venv/bin/python -c "import lightgbm" 2>/dev/null; then
  echo "[demo] 安装 ML 依赖..."
  .venv/bin/pip install -q -r requirements-ml.txt
fi

DEMO_SECIDS="${DEMO_SECIDS:-1.600519,0.000001,0.002594,1.600036}"

echo "[demo] 调优 LGB（${DEMO_SECIDS} × 300 日，embargo 5d，early stopping）..."
.venv/bin/python scripts/train_quant_models.py \
  --lgb \
  --secids "$DEMO_SECIDS" \
  --limit 300 \
  --train-ratio 0.8 \
  --embargo-days 5

echo "[demo] 完成。权重: models/alpha158_lgb.txt"
echo "[demo] OOS 指标: models/alpha158_lgb.metrics.json"
.venv/bin/python scripts/validate_demo_metrics.py
