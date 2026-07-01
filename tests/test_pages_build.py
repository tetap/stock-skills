"""GitHub Pages 构建 smoke。"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build_pages.py"
OUT = ROOT / "docs" / "_site"


class TestPagesBuild(unittest.TestCase):
    def test_build_pages(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(BUILD)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        if proc.returncode != 0 and "markdown" in proc.stderr:
            self.skipTest("未安装 markdown")
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertTrue((OUT / "index.html").is_file())
        self.assertTrue((OUT / "install.html").is_file())
        self.assertTrue((OUT / "static" / "style.css").is_file())
        self.assertTrue((OUT / "assets" / "banner.png").is_file())
        index = (OUT / "index.html").read_text(encoding="utf-8")
        self.assertIn("stock-skills", index)
        self.assertIn("mermaid", index)


if __name__ == "__main__":
    unittest.main()
