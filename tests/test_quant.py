import json
import tempfile
import unittest
from pathlib import Path

from eastmoney.alpha360 import build_alpha360_from_bars
from eastmoney.alpha360_infer import score_alpha360_heuristic
from eastmoney.ml_models import load_lgb_oos_status, model_status, try_lgb158_score
from eastmoney.quant import build_quant_verdict


def _mock_bars(n: int = 65, *, trend: float = 0.1, tail_spike: float = 0) -> list[dict]:
    bars = []
    for i in range(n):
        close = 10.0 + i * trend
        if tail_spike and i >= n - 5:
            close += tail_spike * (i - (n - 5))
        bars.append(
            {
                "date": f"2026-01-{i + 1:02d}",
                "open": close - 0.05,
                "high": close + 0.2,
                "low": close - 0.2,
                "close": close,
                "volume": 1000.0 + i * 10,
                "amount": (1000.0 + i * 10) * close,
            }
        )
    return bars


class TestAlpha360InferV2(unittest.TestCase):
    def test_short_vs_long_divergence(self) -> None:
        bars = _mock_bars(65, trend=-0.25, tail_spike=4.0)
        built = build_alpha360_from_bars(bars[-60:], seq_len=60, include_tensor=True)
        inf = score_alpha360_heuristic(built)
        self.assertGreater(inf["score_5d"], inf["score_60d"])

    def test_scores_have_5d_and_60d(self) -> None:
        built = build_alpha360_from_bars(_mock_bars(60, trend=-0.1), include_tensor=True)
        inf = score_alpha360_heuristic(built)
        self.assertIn("score_5d", inf)
        self.assertIn("score_60d", inf)
        self.assertNotEqual(inf["score"], inf["score_60d"])

    def test_5d_score_capped(self) -> None:
        bars = _mock_bars(65, trend=-0.05, tail_spike=5.0)
        built = build_alpha360_from_bars(bars[-60:], seq_len=60, include_tensor=True)
        inf = score_alpha360_heuristic(built)
        self.assertLessEqual(inf["score_5d"], 85)
        self.assertGreaterEqual(inf["score_5d"], -85)


class TestQuantVerdict(unittest.TestCase):
    def test_pulse_rebound_neutral_158(self) -> None:
        """舒泰神类：158 中性 + 5d 多 + 60d 空。"""
        a158 = {"inference": {"score": -0.5, "verdict": "因子中性"}}
        a360 = {
            "inference": {
                "score": 45,
                "score_5d": 85,
                "score_60d": -36,
                "verdict_5d": "序列偏多",
                "verdict_60d": "序列偏空",
            }
        }
        v = build_quant_verdict(a158, a360)
        self.assertEqual(v["summary"], "反弹脉冲·因子未跟上")
        self.assertIn("158", v["detail"])

    def test_short_improve_158_bullish(self) -> None:
        a158 = {"inference": {"score": 25, "verdict": "因子偏多"}}
        a360 = {"inference": {"score": 10, "score_5d": 35, "score_60d": -40}}
        v = build_quant_verdict(a158, a360)
        self.assertEqual(v["summary"], "短线改善·中线仍弱")

    def test_pulse_when_158_bearish(self) -> None:
        a158 = {"inference": {"score": -25, "verdict": "因子偏空"}}
        a360 = {"inference": {"score": 10, "score_5d": 35, "score_60d": -40}}
        v = build_quant_verdict(a158, a360)
        self.assertEqual(v["summary"], "反弹脉冲·因子未跟上")

    def test_both_bearish_neutral_158(self) -> None:
        """平安银行类：5/60 同偏空 + 158 中性，不得写「表格同向偏空」。"""
        a158 = {"inference": {"score": -11, "verdict": "因子中性"}}
        a360 = {
            "inference": {
                "score": -50,
                "score_5d": -30,
                "score_60d": -40,
                "verdict_5d": "序列偏空",
                "verdict_60d": "序列偏空",
            }
        }
        v = build_quant_verdict(a158, a360)
        self.assertEqual(v["summary"], "量化偏空")
        self.assertIn("尚未极端确认", v["detail"])
        self.assertNotIn("表格与", v["detail"])

    def test_both_bullish_neutral_158(self) -> None:
        """158 中性 + 双序列偏多，不得写「表格与序列同向偏多」。"""
        a158 = {"inference": {"score": 5, "verdict": "因子中性"}}
        a360 = {
            "inference": {
                "score": 40,
                "score_5d": 35,
                "score_60d": 30,
            }
        }
        v = build_quant_verdict(a158, a360)
        self.assertEqual(v["summary"], "序列偏多·因子未确认")
        self.assertNotIn("表格与", v["detail"])

    def test_both_bullish_bearish_158(self) -> None:
        a158 = {"inference": {"score": -30, "verdict": "因子偏空"}}
        a360 = {
            "inference": {"score": 35, "score_5d": 40, "score_60d": 25}
        }
        v = build_quant_verdict(a158, a360)
        self.assertEqual(v["summary"], "序列转强·因子滞后")


class TestMlModels(unittest.TestCase):
    def test_lgb_missing_returns_none(self) -> None:
        self.assertIsNone(try_lgb158_score({"ROC20": 1.0}, model_path="/nonexistent/lgb.txt"))

    def test_model_status_keys(self) -> None:
        st = model_status()
        self.assertIn("alpha158_lightgbm", st)
        self.assertIn("alpha360_tcn", st)
        self.assertIn("oos_status", st)

    def test_oos_status_no_model(self) -> None:
        st = load_lgb_oos_status(model_path="/nonexistent/lgb.txt")
        self.assertFalse(st["available"])
        self.assertIsNone(st["oos_passed"])
        self.assertEqual(st["reason"], "no_model")

    def test_oos_status_passed_from_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / "alpha158_lgb.txt"
            model.write_text("stub", encoding="utf-8")
            metrics = model.with_suffix(".metrics.json")
            metrics.write_text(
                json.dumps(
                    {
                        "best": {
                            "out_of_sample": {"ic": 0.05, "direction_accuracy": 0.55},
                        }
                    }
                ),
                encoding="utf-8",
            )
            st = load_lgb_oos_status(model_path=model)
            self.assertTrue(st["available"])
            self.assertTrue(st["oos_passed"])
            self.assertIsNone(st["report_cap"])

    def test_oos_status_failed_from_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / "alpha158_lgb.txt"
            model.write_text("stub", encoding="utf-8")
            metrics = model.with_suffix(".metrics.json")
            metrics.write_text(
                json.dumps({"best": {"out_of_sample": {"ic": -0.01, "direction_accuracy": 0.48}}}),
                encoding="utf-8",
            )
            st = load_lgb_oos_status(model_path=model)
            self.assertFalse(st["oos_passed"])
            self.assertIn("右侧等待", st["report_cap"])

    def test_bundled_demo_model_oos_not_passed(self) -> None:
        root = Path(__file__).resolve().parents[1]
        model = root / "models" / "alpha158_lgb.txt"
        if not model.is_file():
            self.skipTest("无演示权重")
        st = load_lgb_oos_status(model_path=model)
        self.assertTrue(st["available"])
        self.assertFalse(st["oos_passed"])


if __name__ == "__main__":
    unittest.main()
