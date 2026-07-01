#!/usr/bin/env bash
# 从 CHANGELOG.md 提取指定版本的 Release 正文（stdout）。
# 用法: bash scripts/release_notes.sh v0.1.0
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAG="${1:?用法: release_notes.sh v0.1.0}"

exec python3 "$ROOT/scripts/release_notes.py" "$TAG"
