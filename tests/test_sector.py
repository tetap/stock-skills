import unittest
from unittest.mock import MagicMock, patch

from eastmoney.sector import get_sector_detail


class TestSectorDetail(unittest.TestCase):
    @patch("eastmoney.sector.get_sector_members")
    def test_fund_flow_detail_type(self, mock_members: MagicMock) -> None:
        mock_members.return_value = [{"code": "600519", "main_net_inflow": 100}]
        client = MagicMock()

        result = get_sector_detail(
            client,
            board_code="BK0475",
            board_name="银行",
            detail_type="fund_flow",
            limit=10,
        )

        self.assertEqual(result["detail_type"], "fund_flow")
        self.assertIn("fund_flow", result)
        mock_members.assert_called_once_with(
            client,
            "BK0475",
            limit=10,
            sort_by_fund_flow=True,
        )

    def test_invalid_detail_type(self) -> None:
        client = MagicMock()
        with self.assertRaises(ValueError):
            get_sector_detail(client, board_code="BK0475", detail_type="unknown")


if __name__ == "__main__":
    unittest.main()
