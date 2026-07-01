#!/usr/bin/env python3
"""东方财富工具 CLI。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eastmoney.tools import TOOL_NAMES, run_tool  # noqa: E402


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--secid", help="证券 ID，如 1.600519")
    parser.add_argument("--code", help="6 位股票代码")
    parser.add_argument("--query", help="搜索关键词或名称")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--period", default="daily")
    parser.add_argument("--adjust", default="qfq", choices=["none", "qfq", "hfq"])
    parser.add_argument("--report-type", default="income", choices=["income", "balance", "cashflow"])
    parser.add_argument("--content-type", default="news", choices=["news", "announcement", "report"])
    parser.add_argument("--benchmark-code", default="000300")
    parser.add_argument("--sector-type", default="industry", choices=["industry", "concept"])
    parser.add_argument("--detail-type", default="members", choices=["members", "kline", "fund_flow"])
    parser.add_argument("--board-code")
    parser.add_argument("--board-name")
    parser.add_argument("--sort", default="change_pct")
    parser.add_argument("--indicators", help="逗号分隔，如 ma")
    parser.add_argument("--news-type", default="flash", choices=["flash", "headline", "breakfast"])
    parser.add_argument("--keyword", help="资讯关键词过滤，如 电池、新能源")


def main() -> int:
    parser = argparse.ArgumentParser(description="东方财富数据工具")
    parser.add_argument("tool", choices=TOOL_NAMES + ["list"], help="工具名称")
    _add_common_args(parser)
    args = parser.parse_args()

    if args.tool == "list":
        print(json.dumps(TOOL_NAMES, ensure_ascii=False, indent=2))
        return 0

    kwargs = {
        k: v
        for k, v in {
            "secid": args.secid,
            "code": args.code,
            "query": args.query,
            "limit": args.limit,
            "period": args.period,
            "adjust": args.adjust,
            "report_type": args.report_type,
            "content_type": args.content_type,
            "benchmark_code": args.benchmark_code,
            "sector_type": args.sector_type,
            "detail_type": args.detail_type,
            "board_code": args.board_code,
            "board_name": args.board_name,
            "sort": args.sort,
            "indicators": args.indicators,
            "news_type": args.news_type,
            "keyword": args.keyword,
        }.items()
        if v is not None
    }

    try:
        result = run_tool(args.tool, **kwargs)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
