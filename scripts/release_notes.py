#!/usr/bin/env python3
"""从 CHANGELOG.md 提取指定版本的 Release 正文。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHANGELOG = ROOT / "CHANGELOG.md"


def extract_changelog_section(text: str, version: str) -> str:
    pattern = re.compile(
        rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError(f"CHANGELOG 中未找到版本 [{version}]")
    body = match.group(1).strip()
    body = re.sub(r"^\[[^\]]+\]:[^\n]+\n?", "", body, flags=re.MULTILINE).strip()
    return body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="提取 CHANGELOG 版本段落")
    parser.add_argument("tag", help="如 v0.1.0")
    parser.add_argument(
        "--changelog",
        type=Path,
        default=DEFAULT_CHANGELOG,
    )
    args = parser.parse_args(argv)

    version = args.tag.lstrip("v")
    if not args.changelog.is_file():
        print(f"未找到 {args.changelog}", file=sys.stderr)
        return 1
    try:
        body = extract_changelog_section(
            args.changelog.read_text(encoding="utf-8"),
            version,
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
