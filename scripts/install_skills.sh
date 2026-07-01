#!/usr/bin/env bash
# 兼容旧命令：默认安装到 Cursor 全局目录
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$ROOT/scripts/install.sh" --target cursor --scope user "$@"
