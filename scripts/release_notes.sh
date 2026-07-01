#!/usr/bin/env bash
# 从 CHANGELOG.md 提取指定版本的 Release 正文（stdout）。
# 用法: bash scripts/release_notes.sh v0.1.0
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHANGELOG="${ROOT}/CHANGELOG.md"
TAG="${1:?用法: release_notes.sh v0.1.0}"

# v0.1.0 -> 0.1.0
VERSION="${TAG#v}"

if [[ ! -f "$CHANGELOG" ]]; then
  echo "未找到 CHANGELOG.md" >&2
  exit 1
fi

python3 - "$CHANGELOG" "$VERSION" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
version = sys.argv[2]
text = path.read_text(encoding="utf-8")

pattern = re.compile(
    rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)",
    re.MULTILINE | re.DOTALL,
)
match = pattern.search(text)
if not match:
    print(f"CHANGELOG 中未找到版本 [{version}]", file=sys.stderr)
    sys.exit(1)

body = match.group(1).strip()
# 去掉版本脚注链接行，如 [0.1.0]: https://...
body = re.sub(r"^\[[^\]]+\]:[^\n]+\n?", "", body, flags=re.MULTILINE).strip()
print(body)
PY
