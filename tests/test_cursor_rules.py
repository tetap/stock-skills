"""Cursor 规则与 GitHub 模板存在性。"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / ".cursor" / "rules"

EXPECTED_RULES = (
    "stock-orchestration.mdc",
    "eastmoney-python.mdc",
    "skills-docs.mdc",
)

GITHUB_TEMPLATES = (
    ROOT / ".github" / "pull_request_template.md",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
)


class TestProjectGovernance(unittest.TestCase):
    def test_cursor_rules_present(self) -> None:
        for name in EXPECTED_RULES:
            path = RULES / name
            self.assertTrue(path.is_file(), name)
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---"), name)

    def test_github_templates_present(self) -> None:
        for path in GITHUB_TEMPLATES:
            self.assertTrue(path.is_file(), str(path.relative_to(ROOT)))


if __name__ == "__main__":
    unittest.main()
