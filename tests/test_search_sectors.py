import unittest
from unittest.mock import MagicMock, patch

from eastmoney.sector import search_sectors


class TestSearchSectors(unittest.TestCase):
    @patch("eastmoney.sector.get_sector_overview")
    def test_fuzzy_match(self, mock_overview: MagicMock) -> None:
        mock_overview.side_effect = [
            [
                {"code": "BK001", "name": "电池", "change_pct": 2.5},
                {"code": "BK002", "name": "锂电池", "change_pct": 3.1},
            ],
            [{"code": "BK100", "name": "电池制造", "change_pct": 1.0}],
        ]
        client = MagicMock()

        rows = search_sectors(client, "电池", limit=5)

        self.assertGreaterEqual(len(rows), 2)
        names = {r["name"] for r in rows}
        self.assertIn("电池", names)


if __name__ == "__main__":
    unittest.main()
