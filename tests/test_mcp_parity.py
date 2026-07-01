"""MCP 工具与 eastmoney.tools.TOOL_NAMES 保持一致。"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from eastmoney.tools import TOOL_NAMES

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp_server" / "server.py"


def _mcp_tool_names() -> list[str]:
    text = SERVER.read_text(encoding="utf-8")
    blocks = re.findall(r"@mcp\.tool\(\)\ndef (\w+)\(", text)
    return blocks


class TestMcpToolParity(unittest.TestCase):
    def test_mcp_matches_tool_names(self) -> None:
        mcp_tools = set(_mcp_tool_names()) - {"main"}
        tool_names = set(TOOL_NAMES)
        self.assertEqual(
            mcp_tools,
            tool_names,
            msg=f"MCP only: {sorted(mcp_tools - tool_names)}; "
            f"TOOLS only: {sorted(tool_names - mcp_tools)}",
        )

    def test_count_is_36(self) -> None:
        self.assertEqual(len(TOOL_NAMES), 36)
        self.assertEqual(len(_mcp_tool_names()), 36)


if __name__ == "__main__":
    unittest.main()
