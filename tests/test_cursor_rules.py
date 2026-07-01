"""Cursor 项目规则文件存在性。"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / ".cursor" / "rules"

EXPECTED = (
    "stock-orchestration.mdc",
    "eastmoney-python.mdc",
    "skills-docs.mdc",
)


class TestCursorRules(unittest.TestCase):
    def test_rules_present(self) -> None:
        for name in EXPECTED:
            path = RULES / name
            self.assertTrue(path.is_file(), name)
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---"), name)


if __name__ == "__main__":
    unittest.main()
