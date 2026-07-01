"""演示 LGB metrics 可移植性与 OOS 门槛。"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "models" / "alpha158_lgb.metrics.json"
VALIDATE = ROOT / "scripts" / "validate_demo_metrics.py"


class TestDemoMetrics(unittest.TestCase):
    def test_metrics_model_path_is_relative(self) -> None:
        data = json.loads(METRICS.read_text(encoding="utf-8"))
        model_ref = str(data.get("model") or "")
        self.assertTrue(model_ref)
        self.assertFalse(model_ref.startswith("/"))
        self.assertTrue((ROOT / model_ref).is_file())

    def test_validate_demo_metrics_script(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(VALIDATE)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertIn("OOS 未通过", proc.stdout)

    def test_evaluate_oos_gate(self) -> None:
        from eastmoney.ml_models import evaluate_oos_metrics

        fail = evaluate_oos_metrics({"ic": -0.03, "direction_accuracy": 0.43})
        self.assertFalse(fail["passed"])
        ok = evaluate_oos_metrics({"ic": 0.05, "direction_accuracy": 0.55})
        self.assertTrue(ok["passed"])


if __name__ == "__main__":
    unittest.main()
