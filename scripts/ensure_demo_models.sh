#!/usr/bin/env bash
# 确保演示 LGB 权重存在（本地缺失时从 GitHub 下载或本地训练）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODEL="$ROOT/models/alpha158_lgb.txt"
METRICS="$ROOT/models/alpha158_lgb.metrics.json"
REPO="${STOCK_SKILLS_REPO:-tetap/stock-skills}"
BRANCH="${STOCK_SKILLS_BRANCH:-master}"
BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}/models"

if [[ -f "$MODEL" && -f "$METRICS" ]]; then
  echo "[models] 演示权重已存在: $MODEL"
  exit 0
fi

mkdir -p "$ROOT/models"

download() {
  local name="$1"
  local url="$BASE/$name"
  echo "[models] 下载 $url"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$ROOT/models/$name"
  elif command -v wget >/dev/null 2>&1; then
    wget -q "$url" -O "$ROOT/models/$name"
  else
    echo "需要 curl 或 wget" >&2
    return 1
  fi
}

if download "alpha158_lgb.txt" && download "alpha158_lgb.metrics.json"; then
  echo "[models] 已从 GitHub 拉取演示权重"
  exit 0
fi

echo "[models] 下载失败，尝试本地训练..."
bash "$ROOT/scripts/train_demo_model.sh"
