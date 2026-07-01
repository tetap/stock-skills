"""东方财富 MCP Server。"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated, Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from pydantic import Field  # noqa: E402

from eastmoney.mcp_meta import MCP_INSTRUCTIONS  # noqa: E402
from eastmoney.tools import run_tool  # noqa: E402

Secid = Annotated[str, Field(description="证券 ID，沪 1.xxx 深 0.xxx，如 1.600519")]
Code = Annotated[str, Field(description="6 位 A 股代码，如 600519")]
Query = Annotated[str, Field(description="股票名称或代码，如 贵州茅台 / 600519")]

mcp = FastMCP("eastmoney-stock", instructions=MCP_INSTRUCTIONS)


def _dump(result: Any) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def resolve_symbol(query: Query) -> str:
    """【基础】解析股票名称或代码，返回 secid、code、name。任何分析的第一步。"""
    return _dump(run_tool("resolve_symbol", query=query))


@mcp.tool()
def search_stocks(
    query: Query,
    limit: Annotated[int, Field(description="返回条数", ge=1, le=50)] = 10,
) -> str:
    """【基础】模糊搜索 A 股列表。"""
    return _dump(run_tool("search_stocks", query=query, limit=limit))


@mcp.tool()
def get_realtime_quote(secid: Secid) -> str:
    """【行情】个股实时价、涨跌幅、量额、PE、市值。"""
    return _dump(run_tool("get_realtime_quote", secid=secid))


@mcp.tool()
def get_kline(
    secid: Secid,
    period: Annotated[str, Field(description="daily/weekly/monthly/60min 等")] = "daily",
    adjust: Annotated[str, Field(description="none/qfq/hfq")] = "qfq",
    limit: Annotated[int, Field(ge=1, le=500)] = 120,
) -> str:
    """【行情】K 线历史数据，用于技术面与历史分析。"""
    return _dump(run_tool("get_kline", secid=secid, period=period, adjust=adjust, limit=limit))


@mcp.tool()
def get_market_snapshot(
    sort: Annotated[str, Field(description="change_pct/turnover/volume")] = "change_pct",
    limit: Annotated[int, Field(ge=1, le=100)] = 20,
) -> str:
    """【行情】A 股涨跌榜快照，筛选强势股。"""
    return _dump(run_tool("get_market_snapshot", sort=sort, limit=limit))


@mcp.tool()
def get_company_profile(secid: Secid, code: Code) -> str:
    """【基本面】公司简介、行业、主营业务、上市日期。"""
    return _dump(run_tool("get_company_profile", secid=secid, code=code))


@mcp.tool()
def get_financial_statements(
    code: Code,
    report_type: Annotated[str, Field(description="income/balance/cashflow")] = "income",
    limit: Annotated[int, Field(ge=1, le=20)] = 8,
) -> str:
    """【基本面】利润表/资产负债表/现金流量表。"""
    return _dump(run_tool("get_financial_statements", code=code, report_type=report_type, limit=limit))


@mcp.tool()
def get_valuation_metrics(secid: Secid) -> str:
    """【基本面】PE/PB/总市值/流通市值/换手率。"""
    return _dump(run_tool("get_valuation_metrics", secid=secid))


@mcp.tool()
def get_shareholders(
    code: Code,
    limit: Annotated[int, Field(ge=1, le=30)] = 10,
) -> str:
    """【事件】十大股东及变动。"""
    return _dump(run_tool("get_shareholders", code=code, limit=limit))


@mcp.tool()
def get_shareholder_count(
    code: Code,
    limit: Annotated[int, Field(ge=1, le=20)] = 8,
) -> str:
    """【事件】股东户数趋势：户数、环比变化、户均持股、筹码集中度。"""
    return _dump(run_tool("get_shareholder_count", code=code, limit=limit))


@mcp.tool()
def get_major_events(
    code: Code,
    limit: Annotated[int, Field(ge=1, le=50)] = 20,
) -> str:
    """【事件】大事提醒时间线：报表披露、融资融券、资本运作、分红、股东户数等。"""
    return _dump(run_tool("get_major_events", code=code, limit=limit))


@mcp.tool()
def get_dragon_tiger(
    code: Code,
    limit: Annotated[int, Field(ge=1, le=30)] = 10,
) -> str:
    """【事件】龙虎榜历史记录。"""
    return _dump(run_tool("get_dragon_tiger", code=code, limit=limit))


@mcp.tool()
def get_news_and_reports(
    code: Code,
    content_type: Annotated[str, Field(description="news/announcement/report")] = "news",
    limit: Annotated[int, Field(ge=1, le=30)] = 10,
    source: Annotated[
        str, Field(description="eastmoney=东财搜索, sina=新浪筛选, xueqiu=雪球热度, all=合并(默认)")
    ] = "all",
    stock_name: Annotated[str, Field(description="股票简称，新浪/雪球筛选时使用")] = "",
) -> str:
    """【舆情】个股新闻/公告/研报。新闻已改用东财搜索 API，可合并新浪 7×24 与雪球讨论热度。"""
    kwargs: dict[str, Any] = {
        "code": code,
        "content_type": content_type,
        "limit": limit,
        "source": source,
    }
    if stock_name:
        kwargs["stock_name"] = stock_name
    return _dump(run_tool("get_news_and_reports", **kwargs))


@mcp.tool()
def get_stock_fund_flow(
    secid: Secid,
    limit: Annotated[int, Field(ge=1, le=60)] = 20,
) -> str:
    """【资金面】个股主力/超大单/大单净流入时序。"""
    return _dump(run_tool("get_stock_fund_flow", secid=secid, limit=limit))


@mcp.tool()
def get_fund_flow_rank(limit: Annotated[int, Field(ge=1, le=100)] = 20) -> str:
    """【资金面】全市场主力资金流排名 Top N。"""
    return _dump(run_tool("get_fund_flow_rank", limit=limit))


@mcp.tool()
def get_market_fund_flow(limit: Annotated[int, Field(ge=1, le=60)] = 20) -> str:
    """【资金面】大盘整体主力资金流向背景。"""
    return _dump(run_tool("get_market_fund_flow", limit=limit))


@mcp.tool()
def get_chip_distribution(
    secid: Secid,
    limit: Annotated[int, Field(ge=1, le=120)] = 60,
) -> str:
    """【筹码】获利比例、平均成本、90/70 成本区间与集中度。"""
    return _dump(run_tool("get_chip_distribution", secid=secid, limit=limit))


@mcp.tool()
def get_historical_series(
    secid: Secid,
    period: str = "daily",
    adjust: str = "qfq",
    limit: Annotated[int, Field(ge=30, le=500)] = 250,
    indicators: Annotated[str, Field(description="逗号分隔，如 ma")] = "",
) -> str:
    """【历史】K 线序列 + 涨跌幅/回撤/波动率；可选 MA 指标。"""
    return _dump(
        run_tool(
            "get_historical_series",
            secid=secid,
            period=period,
            adjust=adjust,
            limit=limit,
            indicators=indicators or None,
        )
    )


@mcp.tool()
def compare_performance(
    secid: Secid,
    benchmark_code: Annotated[str, Field(description="基准指数代码，默认沪深300")] = "000300",
    limit: Annotated[int, Field(ge=30, le=500)] = 250,
) -> str:
    """【历史】个股 vs 基准指数的相对收益、回撤、波动。"""
    return _dump(
        run_tool("compare_performance", secid=secid, benchmark_code=benchmark_code, limit=limit)
    )


@mcp.tool()
def get_market_news(
    news_type: Annotated[
        str,
        Field(description="flash/headline/breakfast/sina_roll/sina_live/xueqiu_hot/xueqiu_livenews"),
    ] = "flash",
    keyword: Annotated[str, Field(description="标题/摘要关键词过滤，如 电池、半导体")] = "",
    limit: Annotated[int, Field(ge=1, le=50)] = 20,
    source: Annotated[
        str, Field(description="eastmoney/sina/xueqiu/all，flash 默认 all 合并东财+新浪+雪球热榜")
    ] = "all",
) -> str:
    """【舆情】市场快讯/要闻；source=all 合并东财+新浪+雪球热榜；xueqiu_livenews 需浏览器 Cookie。"""
    kwargs: dict[str, Any] = {"news_type": news_type, "limit": limit, "source": source}
    if keyword:
        kwargs["keyword"] = keyword
    return _dump(run_tool("get_market_news", **kwargs))


@mcp.tool()
def search_sectors(
    query: Annotated[str, Field(description="板块关键词，如 电池、半导体")],
    sector_type: Annotated[str, Field(description="industry/concept，留空则两类都搜")] = "",
    limit: Annotated[int, Field(ge=1, le=20)] = 10,
) -> str:
    """【板块】模糊搜索行业/概念板块名，口语化输入如「电池板块」。"""
    kwargs: dict[str, Any] = {"query": query, "limit": limit}
    if sector_type:
        kwargs["sector_type"] = sector_type
    return _dump(run_tool("search_sectors", **kwargs))


@mcp.tool()
def get_sector_overview(
    sector_type: Annotated[str, Field(description="industry/concept")] = "industry",
    sort: str = "change_pct",
    limit: Annotated[int, Field(ge=1, le=100)] = 30,
) -> str:
    """【板块】行业/概念板块涨跌排行。"""
    return _dump(
        run_tool("get_sector_overview", sector_type=sector_type, sort=sort, limit=limit)
    )


@mcp.tool()
def get_sector_detail(
    board_name: Annotated[str, Field(description="板块名称，如 半导体、银行")] = "",
    board_code: Annotated[str, Field(description="板块代码，如 BK0475")] = "",
    sector_type: Annotated[str, Field(description="industry/concept")] = "industry",
    detail_type: Annotated[str, Field(description="members/kline/fund_flow")] = "members",
    limit: Annotated[int, Field(ge=1, le=200)] = 50,
) -> str:
    """【板块】成分股、板块 K 线、或板块内个股资金流排名。"""
    kwargs: dict[str, Any] = {
        "sector_type": sector_type,
        "detail_type": detail_type,
        "limit": limit,
    }
    if board_name:
        kwargs["board_name"] = board_name
    if board_code:
        kwargs["board_code"] = board_code
    if not board_name and not board_code:
        raise ValueError("board_name 或 board_code 至少提供一个")
    return _dump(run_tool("get_sector_detail", **kwargs))


@mcp.tool()
def get_indicator_interpretation(
    secid: Secid,
    code: Code = "",
    limit: Annotated[int, Field(ge=60, le=500)] = 250,
) -> str:
    """【短线】指标解读：KDJ/RSI/MACD/BIAS 信号近一年回测概率与最新触发。"""
    kwargs: dict[str, Any] = {"secid": secid, "limit": limit}
    if code:
        kwargs["code"] = code
    return _dump(run_tool("get_indicator_interpretation", **kwargs))


@mcp.tool()
def get_limit_up_gene(
    secid: Secid,
    code: Code = "",
    limit: Annotated[int, Field(ge=60, le=500)] = 250,
) -> str:
    """【短线】涨停基因：近一年涨跌停天数、首板封板率、次日红盘率等。"""
    kwargs: dict[str, Any] = {"secid": secid, "limit": limit}
    if code:
        kwargs["code"] = code
    return _dump(run_tool("get_limit_up_gene", **kwargs))


@mcp.tool()
def get_short_term_monitor(code: Code) -> str:
    """【短线】官方涨停基因/短线盯盘（RPT_INTSELECTION_MONITOR，与 App 同源）。"""
    return _dump(run_tool("get_short_term_monitor", code=code))


@mcp.tool()
def get_limit_up_history(
    code: Code,
    limit: Annotated[int, Field(ge=1, le=30)] = 10,
) -> str:
    """【短线】涨跌停历史明细（RPT_INTSELECTION_LIMITUP）。"""
    return _dump(run_tool("get_limit_up_history", code=code, limit=limit))


@mcp.tool()
def get_xueqiu_auth_guide(
    reason: Annotated[
        str,
        Field(description="missing_token=未配置, auth_failed=凭证失效, blocked=WAF拦截"),
    ] = "missing_token",
) -> str:
    """【舆情】雪球登录引导；在 Chrome/Safari 打开 https://xueqiu.com/hq 登录即可（自动读 Cookie）。"""
    return _dump(run_tool("get_xueqiu_auth_guide", reason=reason))


@mcp.tool()
def get_xueqiu_auth_status(
    try_browser: Annotated[bool, Field(description="是否尝试从 Chrome/Safari 读取 Cookie")] = True,
) -> str:
    """【舆情】检测雪球 Cookie 是否可用（环境变量 / 浏览器）。"""
    return _dump(run_tool("get_xueqiu_auth_status", try_browser=try_browser))


@mcp.tool()
def get_xueqiu_data(
    code: Code,
    data_type: Annotated[
        str,
        Field(
            description="report|earningforecast|capital_flow|capital_history|margin|blocktrans|quote|pankou"
        ),
    ] = "report",
    limit: Annotated[int, Field(ge=1, le=50)] = 10,
) -> str:
    """【舆情/数据】pysnowball 雪球接口：研报、盈利预测、资金流向、行情等（需登录 Cookie）。"""
    return _dump(run_tool("get_xueqiu_data", code=code, data_type=data_type, limit=limit))


@mcp.tool()
def get_alpha360_tensor(
    secid: Secid,
    seq_len: Annotated[int, Field(ge=20, le=120, description="时间步长度，默认 60")] = 60,
    include_tensor: Annotated[
        bool,
        Field(description="是否返回完整 6×60 矩阵；默认 false 仅摘要"),
    ] = False,
    period: str = "daily",
    adjust: str = "qfq",
) -> str:
    """【量化】Alpha360 价量张量：6 通道 × seq_len 时间步，供 TCN/LSTM/Transformer 时序模型。"""
    return _dump(
        run_tool(
            "get_alpha360_tensor",
            secid=secid,
            seq_len=seq_len,
            include_tensor=include_tensor,
            period=period,
            adjust=adjust,
        )
    )


@mcp.tool()
def get_alpha360_score(
    secid: Secid,
    seq_len: Annotated[int, Field(ge=20, le=120)] = 60,
    include_tensor: Annotated[bool, Field(description="是否附带完整矩阵")] = False,
    period: str = "daily",
    adjust: str = "qfq",
) -> str:
    """【量化】Alpha360 序列打分：6×60 价量形态 + 启发式分（可选 TCN 权重）。"""
    return _dump(
        run_tool(
            "get_alpha360_score",
            secid=secid,
            seq_len=seq_len,
            include_tensor=include_tensor,
            period=period,
            adjust=adjust,
        )
    )


@mcp.tool()
def get_alpha158_factors(
    secid: Secid,
    include_all_factors: Annotated[bool, Field(description="返回全部因子；默认仅 highlights+summary")] = False,
    period: str = "daily",
    adjust: str = "qfq",
) -> str:
    """【量化】Alpha158 表格因子（158 维价量特征），供 LightGBM 等模型。"""
    return _dump(
        run_tool(
            "get_alpha158_factors",
            secid=secid,
            include_all_factors=include_all_factors,
            period=period,
            adjust=adjust,
        )
    )


@mcp.tool()
def get_alpha158_score(
    secid: Secid,
    include_all_factors: Annotated[bool, Field(description="是否附带全部因子")] = False,
    period: str = "daily",
    adjust: str = "qfq",
) -> str:
    """【量化】Alpha158 因子综合分 + 摘要（表格侧，与 Alpha360 序列分互补）。"""
    return _dump(
        run_tool(
            "get_alpha158_score",
            secid=secid,
            include_all_factors=include_all_factors,
            period=period,
            adjust=adjust,
        )
    )


@mcp.tool()
def get_quant_technical(
    secid: Secid,
    period: str = "daily",
    adjust: str = "qfq",
) -> str:
    """【量化】Alpha158+Alpha360 一次拉齐，含 5/60 日序列分与 quant_verdict。"""
    return _dump(
        run_tool(
            "get_quant_technical",
            secid=secid,
            period=period,
            adjust=adjust,
        )
    )


@mcp.tool()
def get_review_protocol(
    flow: Annotated[str, Field(description="审核流程 B=个股 / C=板块 / D=市场简报")] = "B",
) -> str:
    """【审核】返回多重审核轮次、门禁与 §7 模板要求（配合 review-protocol.md）。"""
    return _dump(run_tool("get_review_protocol", flow=flow))


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
