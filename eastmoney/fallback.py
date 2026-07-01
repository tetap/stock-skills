"""AkShare 降级层：东方财富直连失败时使用。"""

from __future__ import annotations

from typing import Any

try:
    import akshare as ak
except ImportError:  # pragma: no cover
    ak = None


def available() -> bool:
    return ak is not None


def _require_akshare() -> Any:
    if ak is None:
        raise RuntimeError("未安装 akshare，请执行: pip install akshare")
    return ak


def _market(code: str) -> str:
    if code.startswith(("6", "5", "9")):
        return "sh"
    if code.startswith(("4", "8")):
        return "bj"
    return "sz"


def _secid_to_code(secid: str) -> str:
    return secid.split(".", 1)[-1]


def _df_records(df: Any, limit: int | None = None) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []
    if limit:
        df = df.tail(limit) if hasattr(df, "tail") else df.head(limit)
    return df.where(df.notna(), None).to_dict(orient="records")


def run_fallback(name: str, **kwargs: Any) -> Any:
    ak_mod = _require_akshare()

    if name == "resolve_symbol":
        query = kwargs["query"]
        if query.isdigit() or (len(query) == 6 and query.isalnum()):
            code = query.zfill(6)
            market = "1" if code.startswith(("6", "5", "9")) else "0"
            return {"query": query, "code": code, "secid": f"{market}.{code}", "name": None}
        df = ak_mod.stock_info_a_code_name()
        hit = df[df["name"].str.contains(query, na=False)]
        if hit.empty:
            raise ValueError(f"未找到匹配股票: {query}")
        row = hit.iloc[0]
        code = str(row["code"]).zfill(6)
        market = "1" if code.startswith(("6", "5", "9")) else "0"
        return {"query": query, "code": code, "secid": f"{market}.{code}", "name": row["name"]}

    if name == "get_realtime_quote":
        code = _secid_to_code(kwargs["secid"])
        df = ak_mod.stock_bid_ask_em(symbol=code)
        row = {r["item"]: r["value"] for _, r in df.iterrows()}
        return {
            "secid": kwargs["secid"],
            "code": code,
            "name": row.get("名称"),
            "price": _to_float(row.get("最新")),
            "change_pct": _to_float(row.get("涨幅")),
            "change_amount": _to_float(row.get("涨跌")),
            "open": _to_float(row.get("今开")),
            "high": _to_float(row.get("最高")),
            "low": _to_float(row.get("最低")),
            "prev_close": _to_float(row.get("昨收")),
            "volume": _to_float(row.get("总手")),
            "amount": _to_float(row.get("金额")),
            "turnover_rate": _to_float(row.get("换手")),
            "pe_ttm": _to_float(row.get("市盈率-动态")),
            "_data_source": "akshare",
        }

    if name == "get_kline":
        code = _secid_to_code(kwargs["secid"])
        period_map = {
            "daily": "daily",
            "weekly": "weekly",
            "monthly": "monthly",
            "1min": "1",
            "5min": "5",
            "15min": "15",
            "30min": "30",
            "60min": "60",
        }
        period = period_map.get(kwargs.get("period", "daily"), "daily")
        adjust_map = {"none": "", "qfq": "qfq", "hfq": "hfq"}
        adjust = adjust_map.get(kwargs.get("adjust", "qfq"), "qfq")
        if period in {"1", "5", "15", "30", "60"}:
            df = ak_mod.stock_zh_a_hist_min_em(symbol=code, period=period, adjust=adjust)
        else:
            df = ak_mod.stock_zh_a_hist(
                symbol=code,
                period=period,
                adjust=adjust,
                start_date="19900101",
            )
        limit = int(kwargs.get("limit", 120))
        rows = []
        for _, r in df.tail(limit).iterrows():
            rows.append(
                {
                    "date": str(r.get("日期") or r.get("时间")),
                    "open": _to_float(r.get("开盘")),
                    "close": _to_float(r.get("收盘")),
                    "high": _to_float(r.get("最高")),
                    "low": _to_float(r.get("最低")),
                    "volume": _to_float(r.get("成交量")),
                    "amount": _to_float(r.get("成交额")),
                    "change_pct": _to_float(r.get("涨跌幅")),
                    "turnover_rate": _to_float(r.get("换手率")),
                }
            )
        return rows

    if name == "get_stock_fund_flow":
        code = _secid_to_code(kwargs["secid"])
        df = ak_mod.stock_individual_fund_flow(stock=code, market=_market(code))
        limit = int(kwargs.get("limit", 20))
        rows = []
        for _, r in df.tail(limit).iterrows():
            rows.append(
                {
                    "date": str(r.get("日期")),
                    "main_net_inflow": _to_float(r.get("主力净流入-净额")),
                    "main_net_inflow_pct": _to_float(r.get("主力净流入-净占比")),
                    "super_large_net_inflow": _to_float(r.get("超大单净流入-净额")),
                    "large_net_inflow": _to_float(r.get("大单净流入-净额")),
                    "medium_net_inflow": _to_float(r.get("中单净流入-净额")),
                    "small_net_inflow": _to_float(r.get("小单净流入-净额")),
                }
            )
        return rows

    if name == "get_chip_distribution":
        code = _secid_to_code(kwargs["secid"])
        df = ak_mod.stock_cyq_em(symbol=code)
        limit = int(kwargs.get("limit", 60))
        rows = []
        for _, r in df.tail(limit).iterrows():
            rows.append(
                {
                    "date": str(r.get("日期")),
                    "profit_ratio": _to_float(r.get("获利比例")),
                    "avg_cost": _to_float(r.get("平均成本")),
                    "cost_90_low": _to_float(r.get("90成本-低")),
                    "cost_90_high": _to_float(r.get("90成本-高")),
                    "concentration_90": _to_float(r.get("90集中度")),
                    "cost_70_low": _to_float(r.get("70成本-低")),
                    "cost_70_high": _to_float(r.get("70成本-高")),
                    "concentration_70": _to_float(r.get("70集中度")),
                }
            )
        return rows

    if name == "get_sector_overview":
        sector_type = kwargs.get("sector_type", "industry")
        limit = int(kwargs.get("limit", 30))
        if sector_type == "concept":
            df = ak_mod.stock_board_concept_name_em()
        else:
            df = ak_mod.stock_board_industry_name_em()
        sort_col = "涨跌幅" if "涨跌幅" in df.columns else df.columns[-1]
        df = df.sort_values(sort_col, ascending=False).head(limit)
        rows = []
        for _, r in df.iterrows():
            rows.append(
                {
                    "code": r.get("板块代码"),
                    "name": r.get("板块名称"),
                    "change_pct": _to_float(r.get("涨跌幅")),
                    "price": _to_float(r.get("最新价")),
                    "change_amount": _to_float(r.get("涨跌额")),
                    "volume": _to_float(r.get("成交量")),
                    "amount": _to_float(r.get("成交额")),
                    "turnover_rate": _to_float(r.get("换手率")),
                    "up_count": _to_float(r.get("上涨家数")),
                    "down_count": _to_float(r.get("下跌家数")),
                    "leader": r.get("领涨股票"),
                }
            )
        return rows

    if name == "get_sector_detail":
        detail_type = kwargs.get("detail_type", "members")
        sector_type = kwargs.get("sector_type", "industry")
        board_name = kwargs.get("board_name")
        if not board_name:
            raise ValueError("akshare 降级需要 board_name")
        if detail_type == "kline":
            if sector_type == "concept":
                df = ak_mod.stock_board_concept_hist_em(
                    symbol=board_name,
                    period="daily",
                    start_date="20200101",
                    adjust="qfq",
                )
            else:
                df = ak_mod.stock_board_industry_hist_em(
                    symbol=board_name,
                    period="daily",
                    start_date="20200101",
                    adjust="qfq",
                )
            limit = int(kwargs.get("limit", 120))
            rows = []
            for _, r in df.tail(limit).iterrows():
                rows.append(
                    {
                        "date": str(r.get("日期")),
                        "open": _to_float(r.get("开盘")),
                        "close": _to_float(r.get("收盘")),
                        "high": _to_float(r.get("最高")),
                        "low": _to_float(r.get("最低")),
                        "volume": _to_float(r.get("成交量")),
                        "amount": _to_float(r.get("成交额")),
                    }
                )
            return {
                "board_name": board_name,
                "detail_type": detail_type,
                "kline": rows,
                "_data_source": "akshare",
            }
        if detail_type == "fund_flow":
            df = ak_mod.stock_sector_fund_flow_summary(symbol=board_name, indicator="今日")
            limit = int(kwargs.get("limit", 50))
            rows = []
            for _, r in df.head(limit).iterrows():
                rows.append(
                    {
                        "code": r.get("代码") or r.get("股票代码"),
                        "name": r.get("名称") or r.get("股票名称"),
                        "price": _to_float(r.get("最新价")),
                        "change_pct": _to_float(r.get("涨跌幅")),
                        "main_net_inflow": _to_float(r.get("主力净流入-净额")),
                        "main_net_inflow_pct": _to_float(r.get("主力净流入-净占比")),
                    }
                )
            return {
                "board_name": board_name,
                "detail_type": detail_type,
                "fund_flow": rows,
                "_data_source": "akshare",
            }
        if sector_type == "concept":
            df = ak_mod.stock_board_concept_cons_em(symbol=board_name)
        else:
            df = ak_mod.stock_board_industry_cons_em(symbol=board_name)
        limit = int(kwargs.get("limit", 50))
        rows = []
        for _, r in df.head(limit).iterrows():
            rows.append(
                {
                    "code": r.get("代码"),
                    "name": r.get("名称"),
                    "price": _to_float(r.get("最新价")),
                    "change_pct": _to_float(r.get("涨跌幅")),
                    "total_market_cap": _to_float(r.get("总市值")),
                }
            )
        return {
            "board_name": board_name,
            "detail_type": detail_type,
            "members": rows,
            "_data_source": "akshare",
        }

    if name == "get_fund_flow_rank":
        df = ak_mod.stock_individual_fund_flow_rank(indicator="今日")
        limit = int(kwargs.get("limit", 20))
        rows = []
        for _, r in df.head(limit).iterrows():
            rows.append(
                {
                    "code": r.get("代码"),
                    "name": r.get("名称"),
                    "price": _to_float(r.get("最新价")),
                    "change_pct": _to_float(r.get("涨跌幅")),
                    "main_net_inflow": _to_float(r.get("主力净流入-净额")),
                    "main_net_inflow_pct": _to_float(r.get("主力净流入-净占比")),
                }
            )
        return rows

    if name == "get_market_fund_flow":
        df = ak_mod.stock_market_fund_flow()
        limit = int(kwargs.get("limit", 20))
        rows = []
        for _, r in df.tail(limit).iterrows():
            rows.append(
                {
                    "date": str(r.get("日期")),
                    "main_net_inflow": _to_float(r.get("主力净流入-净额")),
                    "main_net_inflow_pct": _to_float(r.get("主力净流入-净占比")),
                    "super_large_net_inflow": _to_float(r.get("超大单净流入-净额")),
                    "large_net_inflow": _to_float(r.get("大单净流入-净额")),
                    "medium_net_inflow": _to_float(r.get("中单净流入-净额")),
                    "small_net_inflow": _to_float(r.get("小单净流入-净额")),
                }
            )
        return rows

    raise NotImplementedError(f"akshare 降级暂未支持: {name}")


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if isinstance(value, str):
            value = value.replace(",", "").replace("%", "")
        return float(value)
    except (TypeError, ValueError):
        return None
