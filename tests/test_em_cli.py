import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestEmCli(unittest.TestCase):
    def test_get_review_protocol_flow_c(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "em.py"),
                "get_review_protocol",
                "--flow",
                "C",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn('"flow": "C"', proc.stdout)


if __name__ == "__main__":
    unittest.main()
