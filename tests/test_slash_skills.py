"""agent-slash-skills 结构完整性。"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLASH = ROOT / "agent-slash-skills"

EXPECTED = {
    "stock",
    "stock-analyze",
    "stock-market",
    "stock-fund",
    "stock-chip",
    "stock-kline",
    "stock-basic",
    "stock-sector",
    "stock-news",
}


class TestSlashSkillsLayout(unittest.TestCase):
    def test_all_slash_skills_present(self) -> None:
        names = {p.name for p in SLASH.iterdir() if p.is_dir()}
        self.assertTrue(EXPECTED.issubset(names), msg=sorted(EXPECTED - names))

    def test_skill_and_openai_yaml(self) -> None:
        for name in sorted(EXPECTED):
            base = SLASH / name
            self.assertTrue((base / "SKILL.md").is_file(), name)
            self.assertTrue((base / "agents" / "openai.yaml").is_file(), name)


if __name__ == "__main__":
    unittest.main()
