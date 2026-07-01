"""Cursor 规则与 GitHub 模板存在性。"""

from __future__ import annotations

import subprocess
import sys
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

GOVERNANCE_DOCS = (
    ROOT / "AGENTS.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "SECURITY.md",
    ROOT / "CHANGELOG.md",
    ROOT / "ROADMAP.md",
)

GUIDE_DOCS: tuple[Path, ...] = ()

README_ASSETS = (
    ROOT / "docs" / "assets" / "banner.png",
)

RELEASE_NOTES_SCRIPT = ROOT / "scripts" / "release_notes.py"


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

    def test_governance_docs_present(self) -> None:
        for path in GOVERNANCE_DOCS:
            self.assertTrue(path.is_file(), str(path.relative_to(ROOT)))

    def test_guide_docs_present(self) -> None:
        for path in GUIDE_DOCS:
            self.assertTrue(path.is_file(), str(path.relative_to(ROOT)))

    def test_readme_assets_present(self) -> None:
        for path in README_ASSETS:
            self.assertTrue(path.is_file(), str(path.relative_to(ROOT)))

    def test_release_notes_extracts_version(self) -> None:
        self.assertTrue(RELEASE_NOTES_SCRIPT.is_file())

        proc = subprocess.run(
            [sys.executable, str(RELEASE_NOTES_SCRIPT), "v0.1.0"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("MCP", proc.stdout)
        self.assertIn("OOS 未通过", proc.stdout)


if __name__ == "__main__":
    unittest.main()
