"""指标解读、涨停基因等短线统计（基于 K 线本地回测，对齐 App 展示逻辑）。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.kline import get_kline


def _limit_threshold(code: str | None) -> float:
    if not code:
        return 9.9
    if code.startswith(("300", "688")):
        return 19.5
    if code.startswith(("8", "4")):
        return 29.9
    return 9.9


def _ema_series(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (span + 1)
    out = [values[0]]
    for v in values[1:]:
        out.append(alpha * v + (1 - alpha) * out[-1])
    return out


def _kdj(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    n: int = 9,
) -> tuple[list[float], list[float], list[float]]:
    k_val, d_val = 50.0, 50.0
    ks, ds, js = [], [], []
    for i in range(len(closes)):
        start = max(0, i - n + 1)
        hh = max(highs[start : i + 1])
        ll = min(lows[start : i + 1])
        if hh == ll:
            rsv = 50.0
        else:
            rsv = (closes[i] - ll) / (hh - ll) * 100
        k_val = k_val * 2 / 3 + rsv / 3
        d_val = d_val * 2 / 3 + k_val / 3
        j_val = 3 * k_val - 2 * d_val
        ks.append(k_val)
        ds.append(d_val)
        js.append(j_val)
    return ks, ds, js


def _rsi(closes: list[float], n: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(closes)
    if len(closes) <= n:
        return out
    gains, losses = [], []
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i - 1]
        gains.append(max(ch, 0))
        losses.append(max(-ch, 0))
    avg_gain = sum(gains[:n]) / n
    avg_loss = sum(losses[:n]) / n
    out[n] = 100.0 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss)
    for i in range(n + 1, len(closes)):
        avg_gain = (avg_gain * (n - 1) + gains[i - 1]) / n
        avg_loss = (avg_loss * (n - 1) + losses[i - 1]) / n
        out[i] = 100.0 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss)
    return out


def _macd(closes: list[float]) -> tuple[list[float], list[float], list[float]]:
    ema12 = _ema_series(closes, 12)
    ema26 = _ema_series(closes, 26)
    dif = [a - b for a, b in zip(ema12, ema26)]
    dea = _ema_series(dif, 9)
    hist = [d - e for d, e in zip(dif, dea)]
    return dif, dea, hist


def _bias(closes: list[float], n: int = 6) -> list[float | None]:
    out: list[float | None] = []
    for i in range(len(closes)):
        if i + 1 < n:
            out.append(None)
            continue
        ma = sum(closes[i + 1 - n : i + 1]) / n
        out.append((closes[i] / ma - 1) * 100 if ma else None)
    return out


def _backtest_signal(
    closes: list[float],
    dates: list[str],
    signal_indices: list[int],
    *,
    horizons: tuple[int, ...] = (1, 10),
) -> dict[str, Any]:
    stats: dict[str, Any] = {"occurrences": len(signal_indices), "horizons": {}}
    for h in horizons:
        rets: list[float] = []
        for idx in signal_indices:
            if idx + h >= len(closes) or closes[idx] == 0:
                continue
            rets.append((closes[idx + h] / closes[idx] - 1) * 100)
        if not rets:
            stats["horizons"][f"{h}d"] = None
            continue
        stats["horizons"][f"{h}d"] = {
            "rise_probability_pct": round(sum(1 for r in rets if r > 0) / len(rets) * 100, 2),
            "avg_change_pct": round(sum(rets) / len(rets), 2),
            "sample_size": len(rets),
        }
    if signal_indices:
        last = signal_indices[-1]
        stats["latest"] = {
            "date": dates[last],
            "change_since_pct": round((closes[-1] / closes[last] - 1) * 100, 2) if closes[last] else None,
        }
    return stats


def _collect_kdj_signals(ks: list[float], ds: list[float], js: list[float]) -> dict[str, list[int]]:
    golden, oversold, overbought = [], [], []
    for i in range(1, len(ks)):
        if ks[i - 1] <= ds[i - 1] and ks[i] > ds[i]:
            golden.append(i)
        if js[i] < 0 or (ks[i] < 20 and ds[i] < 20):
            oversold.append(i)
        if js[i] > 100 or (ks[i] > 80 and ds[i] > 80):
            overbought.append(i)
    return {"kdj_golden_cross": golden, "kdj_oversold": oversold, "kdj_overbought": overbought}


def _collect_rsi_signals(rsi: list[float | None]) -> dict[str, list[int]]:
    oversold, overbought = [], []
    for i, v in enumerate(rsi):
        if v is None:
            continue
        if v < 30:
            oversold.append(i)
        elif v > 70:
            overbought.append(i)
    return {"rsi_oversold": oversold, "rsi_overbought": overbought}


def _collect_macd_signals(dif: list[float], dea: list[float]) -> dict[str, list[int]]:
    golden, death = [], []
    for i in range(1, len(dif)):
        if dif[i - 1] <= dea[i - 1] and dif[i] > dea[i]:
            golden.append(i)
        if dif[i - 1] >= dea[i - 1] and dif[i] < dea[i]:
            death.append(i)
    return {"macd_golden_cross": golden, "macd_death_cross": death}


def _collect_bias_signals(bias: list[float | None], threshold: float = -6.0) -> dict[str, list[int]]:
    oversold, overbought = [], []
    for i, v in enumerate(bias):
        if v is None:
            continue
        if v <= threshold:
            oversold.append(i)
        elif v >= -threshold:
            overbought.append(i)
    return {"bias_oversold": oversold, "bias_overbought": overbought}


def get_indicator_interpretation(
    client: EastMoneyClient,
    secid: str,
    *,
    code: str | None = None,
    limit: int = 250,
) -> dict[str, Any]:
    """指标解读：KDJ/RSI/MACD/BIAS 信号历史回测统计（对齐 App「指标解读」）。"""
    rows = get_kline(client, secid, limit=limit)
    if len(rows) < 30:
        return {"secid": secid, "error": "K 线数据不足", "signals": {}}

    dates = [r["date"] for r in rows]
    closes = [r["close"] for r in rows]
    highs = [r["high"] for r in rows]
    lows = [r["low"] for r in rows]

    ks, ds, js = _kdj(highs, lows, closes)
    rsi = _rsi(closes)
    dif, dea, _ = _macd(closes)
    bias6 = _bias(closes, 6)

    all_signals: dict[str, list[int]] = {}
    all_signals.update(_collect_kdj_signals(ks, ds, js))
    all_signals.update(_collect_rsi_signals(rsi))
    all_signals.update(_collect_macd_signals(dif, dea))
    all_signals.update(_collect_bias_signals(bias6))

    interpreted: dict[str, Any] = {}
    for name, indices in all_signals.items():
        if not indices:
            continue
        stat = _backtest_signal(closes, dates, indices)
        if stat["latest"] and closes[indices[-1]]:
            stat["latest"]["change_since_pct"] = round(
                (closes[-1] / closes[indices[-1]] - 1) * 100, 2
            )
        interpreted[name] = stat

    return {
        "secid": secid,
        "code": code,
        "lookback_bars": len(rows),
        "period_start": dates[0],
        "period_end": dates[-1],
        "latest_values": {
            "kdj_k": round(ks[-1], 2),
            "kdj_d": round(ds[-1], 2),
            "kdj_j": round(js[-1], 2),
            "rsi14": round(rsi[-1], 2) if rsi[-1] is not None else None,
            "macd_dif": round(dif[-1], 4),
            "macd_dea": round(dea[-1], 4),
            "bias6": round(bias6[-1], 2) if bias6[-1] is not None else None,
        },
        "signals": interpreted,
        "_note": "基于近一年 K 线本地回测，概率为历史统计非预测",
    }


def get_limit_up_gene(
    client: EastMoneyClient,
    secid: str,
    *,
    code: str | None = None,
    limit: int = 250,
) -> dict[str, Any]:
    """涨停基因：近一年涨跌停统计（对齐 App「涨停雷达」）。"""
    rows = get_kline(client, secid, limit=limit)
    threshold = _limit_threshold(code)
    if len(rows) < 20:
        return {"secid": secid, "error": "K 线数据不足"}

    limit_up_days: list[dict[str, Any]] = []
    limit_down_days: list[str] = []
    premium_5_days = 0
    first_board_total = 0
    first_board_sealed = 0
    next_day_red = 0
    next_day_total = 0
    consecutive_after = 0
    consecutive_total = 0

    for i, row in enumerate(rows):
        ch = row.get("change_pct")
        if ch is None:
            continue
        if ch >= threshold - 0.1:
            prev_limit = i > 0 and (rows[i - 1].get("change_pct") or 0) >= threshold - 0.1
            high, close = row["high"], row["close"]
            sealed = high > 0 and abs(close - high) / high < 0.002
            limit_up_days.append({"date": row["date"], "change_pct": ch, "first_board": not prev_limit})

            if not prev_limit:
                first_board_total += 1
                if sealed:
                    first_board_sealed += 1

            if i + 1 < len(rows):
                next_day_total += 1
                nxt = rows[i + 1]
                if (nxt.get("change_pct") or 0) > 0:
                    next_day_red += 1
                if (nxt.get("change_pct") or 0) >= 5:
                    premium_5_days += 1
                if (nxt.get("change_pct") or 0) >= threshold - 0.1:
                    consecutive_after += 1
                consecutive_total += 1

        elif ch <= -(threshold - 0.1):
            limit_down_days.append(row["date"])

    return {
        "secid": secid,
        "code": code,
        "limit_threshold_pct": threshold,
        "period_start": rows[0]["date"],
        "period_end": rows[-1]["date"],
        "limit_up_days": len(limit_up_days),
        "limit_down_days": len(limit_down_days),
        "premium_5pct_days": premium_5_days,
        "limit_up_success_rate_pct": round(
            len([d for d in limit_up_days if d.get("change_pct", 0) >= threshold - 0.1])
            / max(len(limit_up_days), 1)
            * 100,
            2,
        ),
        "first_board_seal_rate_pct": round(
            first_board_sealed / first_board_total * 100, 2
        )
        if first_board_total
        else None,
        "next_day_positive_rate_pct": round(next_day_red / next_day_total * 100, 2)
        if next_day_total
        else None,
        "consecutive_limit_up_rate_pct": round(consecutive_after / consecutive_total * 100, 2)
        if consecutive_total
        else None,
        "details": limit_up_days[-10:],
        "_note": "基于 K 线涨跌幅近似识别涨跌停，与 App 口径可能略有差异",
    }
