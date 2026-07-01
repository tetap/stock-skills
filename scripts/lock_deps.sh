#!/usr/bin/env bash
# 从当前 .venv 导出 requirements.lock（主依赖精确版本）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/pip ]]; then
  echo "请先创建 .venv 并安装 requirements.txt" >&2
  exit 1
fi

PKGS=(requests pandas akshare curl_cffi mcp pysnowball browser-cookie3)
ML=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ml) ML=true; shift ;;
    *) echo "未知参数: $1" >&2; exit 1 ;;
  esac
done

if [[ "$ML" == "true" ]]; then
  PKGS=(lightgbm numpy torch)
  LOCK="$ROOT/requirements-ml.lock"
  HEADER="# ML 依赖锁定（可选，配合 --with-ml）"
else
  LOCK="$ROOT/requirements.lock"
  HEADER="# 锁定主依赖版本（可复现安装）"
fi

{
  echo "$HEADER"
  echo "# 重新生成: bash scripts/lock_deps.sh$([[ "$ML" == true ]] && echo ' --ml')"
  echo
  .venv/bin/pip freeze | grep -iE "^($(IFS='|'; echo "${PKGS[*]}"))=="
} > "$LOCK"
echo "已写入 $LOCK"
