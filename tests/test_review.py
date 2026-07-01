import unittest

from eastmoney.review import get_review_protocol
from eastmoney.tools import TOOL_NAMES, run_tool


class TestReviewProtocol(unittest.TestCase):
    def test_flow_b_rounds(self) -> None:
        proto = get_review_protocol(flow="B")
        self.assertEqual(proto["flow"], "B")
        self.assertGreaterEqual(proto["min_tool_calls"], 20)
        ids = [r["id"] for r in proto["rounds"]]
        self.assertIn("R0", ids)
        self.assertIn("R6", ids)

    def test_invalid_flow(self) -> None:
        with self.assertRaises(ValueError):
            get_review_protocol(flow="X")

    def test_run_tool_review(self) -> None:
        result = run_tool("get_review_protocol", flow="C")
        self.assertEqual(result["flow"], "C")
        self.assertIn("search_sectors", result["required_tools"])

    def test_flow_d_required_tools(self) -> None:
        proto = get_review_protocol(flow="D")
        self.assertEqual(proto["min_tool_calls"], 8)
        self.assertIn("get_market_snapshot", proto["required_tools"])
        self.assertIn("get_market_news", proto["required_tools"])


class TestToolCount(unittest.TestCase):
    def test_tool_names_count(self) -> None:
        self.assertEqual(len(TOOL_NAMES), 33)
        self.assertIn("get_review_protocol", TOOL_NAMES)
        self.assertIn("get_alpha158_score", TOOL_NAMES)


if __name__ == "__main__":
    unittest.main()
