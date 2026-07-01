import unittest

from eastmoney.historical import _max_drawdown, _period_return, _volatility


class TestHistoricalMetrics(unittest.TestCase):
    def test_period_return(self) -> None:
        self.assertEqual(_period_return([100, 110]), 10.0)
        self.assertIsNone(_period_return([]))

    def test_max_drawdown(self) -> None:
        self.assertEqual(_max_drawdown([100, 120, 90]), 25.0)

    def test_volatility(self) -> None:
        vol = _volatility([0.01, -0.01, 0.02, -0.02])
        self.assertIsNotNone(vol)
        assert vol is not None
        self.assertGreater(vol, 0)


if __name__ == "__main__":
    unittest.main()
