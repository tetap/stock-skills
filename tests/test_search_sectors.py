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

    @patch("eastmoney.sector.get_sector_overview")
    def test_empty_query_returns_empty(self, mock_overview: MagicMock) -> None:
        client = MagicMock()
        self.assertEqual(search_sectors(client, "  "), [])
        mock_overview.assert_not_called()

    @patch("eastmoney.sector.get_sector_overview")
    def test_sector_type_filter(self, mock_overview: MagicMock) -> None:
        mock_overview.return_value = [
            {"code": "BK001", "name": "半导体", "change_pct": 1.0},
        ]
        client = MagicMock()

        rows = search_sectors(client, "半导", sector_type="industry", limit=5)

        mock_overview.assert_called_once()
        self.assertEqual(mock_overview.call_args.kwargs["sector_type"], "industry")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["sector_type"], "industry")

    @patch("eastmoney.sector.get_sector_overview")
    def test_exact_match_scores_higher(self, mock_overview: MagicMock) -> None:
        mock_overview.side_effect = [
            [
                {"code": "BK001", "name": "电池", "change_pct": 1.0},
                {"code": "BK002", "name": "锂电池", "change_pct": 5.0},
            ],
            [],
        ]
        client = MagicMock()

        rows = search_sectors(client, "电池", limit=5)

        self.assertEqual(rows[0]["name"], "电池")
        self.assertEqual(rows[0]["match_score"], 100)

    @patch("eastmoney.sector.get_sector_overview")
    def test_deduplicates_across_types(self, mock_overview: MagicMock) -> None:
        mock_overview.side_effect = [
            [{"code": "BK001", "name": "人工智能", "change_pct": 1.0}],
            [{"code": "BK001", "name": "人工智能", "change_pct": 1.0}],
        ]
        client = MagicMock()

        rows = search_sectors(client, "人工智能", limit=10)

        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
