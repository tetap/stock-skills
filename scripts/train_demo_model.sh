#!/usr/bin/env bash
# 训练演示用 Alpha158 LightGBM（小样本、无网格，约 1~3 分钟）
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

echo "[demo] 训练演示 LGB（2 股 × 200 日 K 线，80/20 OOS，慢速限流）..."
.venv/bin/python scripts/train_quant_models.py \
  --lgb \
  --secids "1.600519,0.000001" \
  --limit 200 \
  --train-ratio 0.8

echo "[demo] 完成。权重: models/alpha158_lgb.txt"
echo "[demo] OOS 指标: models/alpha158_lgb.metrics.json"
.venv/bin/python scripts/validate_demo_metrics.py
