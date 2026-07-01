"""Alpha158 表格因子（Qlib 风格）：158 个价量工程特征，供 LightGBM 等表格模型。"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from eastmoney.alpha360 import _vwap
from eastmoney.client import EastMoneyClient
from eastmoney.kline import get_kline

WINDOWS = (5, 10, 20, 30, 60)
MIN_BARS = 61


def _bars_to_frame(bars: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(bars)
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = df[col].astype(float)
    df["vwap"] = [_vwap(b) for b in bars]
    return df


def _slope(values: np.ndarray) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    x = np.arange(n, dtype=float)
    y = values.astype(float)
    x_mean = x.mean()
    y_mean = y.mean()
    den = ((x - x_mean) ** 2).sum()
    if den == 0:
        return 0.0
    return float(((x - x_mean) * (y - y_mean)).sum() / den)


def _rsquare(values: np.ndarray) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    x = np.arange(n, dtype=float)
    y = values.astype(float)
    slope = _slope(y)
    intercept = y.mean() - slope * x.mean()
    pred = slope * x + intercept
    ss_res = ((y - pred) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    if ss_tot == 0:
        return 0.0
    return float(1 - ss_res / ss_tot)


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2:
        return 0.0
    if np.std(a) == 0 or np.std(b) == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def compute_alpha158_from_frame(df: pd.DataFrame) -> dict[str, float]:
    """计算最新一根 K 线上的 Alpha158 因子（与 Qlib Alpha158DL 公式对齐）。"""
    if len(df) < MIN_BARS:
        raise ValueError(f"K 线不足 {MIN_BARS} 根，当前 {len(df)} 根")

    o = df["open"].values
    h = df["high"].values
    l = df["low"].values
    c = df["close"].values
    v = df["volume"].values
    vw = df["vwap"].values

    cur_o, cur_h, cur_l, cur_c, cur_v = o[-1], h[-1], l[-1], c[-1], v[-1]
    if cur_o == 0 or cur_c == 0:
        raise ValueError("最新 OHLC 无效")

    factors: dict[str, float] = {}
    hl_range = cur_h - cur_l + 1e-12

    # K 线形态（9）
    factors["KMID"] = (cur_c - cur_o) / cur_o
    factors["KLEN"] = (cur_h - cur_l) / cur_o
    factors["KMID2"] = (cur_c - cur_o) / hl_range
    factors["KUP"] = (cur_h - max(cur_o, cur_c)) / cur_o
    factors["KUP2"] = (cur_h - max(cur_o, cur_c)) / hl_range
    factors["KLOW"] = (min(cur_o, cur_c) - cur_l) / cur_o
    factors["KLOW2"] = (min(cur_o, cur_c) - cur_l) / hl_range
    factors["KSFT"] = (2 * cur_c - cur_h - cur_l) / cur_o
    factors["KSFT2"] = (2 * cur_c - cur_h - cur_l) / hl_range

    # 当日价量（5）
    factors["OPEN0"] = cur_o / cur_c
    factors["HIGH0"] = cur_h / cur_c
    factors["LOW0"] = cur_l / cur_c
    factors["VWAP0"] = vw[-1] / cur_c
    factors["VOLUME0"] = 1.0

    c_ret = np.diff(c) / (c[:-1] + 1e-12)
    v_log = np.log(v + 1)
    v_chg_log = np.log(v[1:] / (v[:-1] + 1e-12) + 1)

    for d in WINDOWS:
        w_c = c[-d:]
        w_h = h[-d:]
        w_l = l[-d:]
        w_v = v[-d:]
        w_vlog = v_log[-d:]

        factors[f"ROC{d}"] = c[-d - 1] / cur_c if len(c) > d else c[0] / cur_c
        factors[f"MA{d}"] = w_c.mean() / cur_c
        factors[f"STD{d}"] = w_c.std(ddof=0) / cur_c
        factors[f"BETA{d}"] = _slope(w_c) / cur_c
        factors[f"RSQR{d}"] = _rsquare(w_c)
        pred = _slope(w_c) * (np.arange(d) - (d - 1) / 2) + w_c.mean()
        factors[f"RESI{d}"] = (cur_c - pred[-1]) / cur_c
        factors[f"MAX{d}"] = w_h.max() / cur_c
        factors[f"MIN{d}"] = w_l.min() / cur_c
        factors[f"QTLU{d}"] = np.quantile(w_c, 0.8) / cur_c
        factors[f"QTLD{d}"] = np.quantile(w_c, 0.2) / cur_c
        factors[f"RANK{d}"] = float((w_c <= cur_c).sum() / d)
        hl_d = w_h.max() - w_l.min() + 1e-12
        factors[f"RSV{d}"] = (cur_c - w_l.min()) / hl_d
        factors[f"IMAX{d}"] = float(np.argmax(w_h)) / d
        factors[f"IMIN{d}"] = float(np.argmin(w_l)) / d
        factors[f"IMXD{d}"] = (np.argmax(w_h) - np.argmin(w_l)) / d
        factors[f"CORR{d}"] = _corr(w_c, w_vlog)
        if len(c_ret) >= d:
            factors[f"CORD{d}"] = _corr(c_ret[-d:], v_chg_log[-d:])
        else:
            factors[f"CORD{d}"] = _corr(c_ret, v_chg_log[: len(c_ret)])

        up = (w_c[1:] > w_c[:-1]).mean() if d > 1 else 0.0
        down = (w_c[1:] < w_c[:-1]).mean() if d > 1 else 0.0
        factors[f"CNTP{d}"] = float(up)
        factors[f"CNTN{d}"] = float(down)
        factors[f"CNTD{d}"] = float(up - down)

        abs_chg = np.abs(np.diff(w_c))
        gain = np.maximum(np.diff(w_c), 0)
        loss = np.maximum(-np.diff(w_c), 0)
        abs_sum = abs_chg.sum() + 1e-12
        factors[f"SUMP{d}"] = float(gain.sum() / abs_sum)
        factors[f"SUMN{d}"] = float(loss.sum() / abs_sum)
        factors[f"SUMD{d}"] = float((gain.sum() - loss.sum()) / abs_sum)

        factors[f"VMA{d}"] = w_v.mean() / (cur_v + 1e-12)
        factors[f"VSTD{d}"] = w_v.std(ddof=0) / (cur_v + 1e-12)
        w_ret_abs_v = np.abs(np.diff(w_c) / (w_c[:-1] + 1e-12)) * w_v[1:]
        if len(w_ret_abs_v) > 0:
            factors[f"WVMA{d}"] = w_ret_abs_v.std(ddof=0) / (w_ret_abs_v.mean() + 1e-12)
        else:
            factors[f"WVMA{d}"] = 0.0

        v_diff = np.diff(w_v)
        v_gain = np.maximum(v_diff, 0)
        v_loss = np.maximum(-v_diff, 0)
        v_abs = np.abs(v_diff).sum() + 1e-12
        factors[f"VSUMP{d}"] = float(v_gain.sum() / v_abs)
        factors[f"VSUMN{d}"] = float(v_loss.sum() / v_abs)
        factors[f"VSUMD{d}"] = float((v_gain.sum() - v_loss.sum()) / v_abs)

    return {k: round(float(v), 6) if v is not None and not math.isnan(v) else 0.0 for k, v in factors.items()}


def _factor_summary(factors: dict[str, float]) -> dict[str, Any]:
    """提炼报告用摘要。"""
    def g(name: str) -> float | None:
        return factors.get(name)

    momentum = {
        f"ROC{w}": g(f"ROC{w}") for w in (5, 20, 60) if g(f"ROC{w}") is not None
    }
    trend = {
        f"MA{w}": g(f"MA{w}") for w in (5, 20, 60) if g(f"MA{w}") is not None
    }
    sentiment = {
        **{f"CNTP{w}": g(f"CNTP{w}") for w in (5, 20) if g(f"CNTP{w}") is not None},
        **{f"SUMD{w}": g(f"SUMD{w}") for w in (5, 20) if g(f"SUMD{w}") is not None},
    }
    volume = {
        **{f"CORR{w}": g(f"CORR{w}") for w in (10, 20) if g(f"CORR{w}") is not None},
        **{f"VMA{w}": g(f"VMA{w}") for w in (5, 20) if g(f"VMA{w}") is not None},
    }
    volatility = {f"STD{w}": g(f"STD{w}") for w in (10, 20, 60) if g(f"STD{w}") is not None}

    ma20 = g("MA20") or 1.0
    price_vs_ma20_pct = round((1 / ma20 - 1) * 100, 2) if ma20 else None

    return {
        "kbar": {k: factors[k] for k in ("KMID", "KLEN", "KMID2", "KUP", "KUP2", "KLOW", "KLOW2", "KSFT", "KSFT2") if k in factors},
        "momentum": momentum,
        "trend": trend,
        "sentiment": sentiment,
        "volume": volume,
        "volatility": volatility,
        "price_vs_ma20_pct": price_vs_ma20_pct,
    }


def score_alpha158_heuristic(factors: dict[str, float]) -> dict[str, Any]:
    """基于关键 Alpha158 因子的表格侧打分（非 LightGBM 训练权重）。"""
    def clamp(x: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, x))

    roc20 = (1 - (factors.get("ROC20") or 1)) * 100
    ma5 = factors.get("MA5") or 1
    ma20 = factors.get("MA20") or 1
    ma_bias = (ma5 - ma20) * 100
    cntp20 = ((factors.get("CNTP20") or 0.5) - 0.5) * 100
    sumd20 = (factors.get("SUMD20") or 0) * 50
    corr20 = (factors.get("CORR20") or 0) * 25
    std20 = (factors.get("STD20") or 0) * -500

    raw = roc20 * 0.35 + ma_bias * 0.25 + cntp20 * 0.15 + sumd20 * 0.15 + corr20 * 0.1 + std20 * 0.05
    score = round(100 * math.tanh(raw / 35), 2)

    if score >= 20:
        verdict = "因子偏多"
    elif score <= -20:
        verdict = "因子偏空"
    else:
        verdict = "因子中性"

    return {
        "method": "heuristic",
        "score": score,
        "verdict": verdict,
        "drivers": {
            "roc20_pct": round(roc20, 2),
            "ma5_vs_ma20_pct": round(ma_bias, 2),
            "cntp20": factors.get("CNTP20"),
            "sumd20": factors.get("SUMD20"),
            "corr20": factors.get("CORR20"),
        },
        "interpretation": f"Alpha158 表格因子综合 {score}（{verdict}），适合与 Alpha360 序列分交叉验证",
        "_note": "启发式因子分，非 Qlib LightGBM 模型输出",
    }


def score_alpha158(factors: dict[str, float]) -> dict[str, Any]:
    """优先 LightGBM 权重，否则启发式。"""
    from eastmoney.ml_models import try_lgb158_score

    lgb = try_lgb158_score(factors)
    if lgb:
        return lgb
    return score_alpha158_heuristic(factors)


def build_alpha158_from_bars(
    bars: list[dict[str, Any]],
    *,
    include_all_factors: bool = False,
) -> dict[str, Any]:
    df = _bars_to_frame(bars)
    factors = compute_alpha158_from_frame(df)
    result: dict[str, Any] = {
        "factor_count": len(factors),
        "factor_count_note": "Qlib Alpha158 对齐 158 项 + RANK 窗口共 159 个字段",
        "latest_date": str(bars[-1]["date"]),
        "usage": "表格因子 → LightGBM/Linear/TabNet；勿 reshape 为时序张量",
        "summary": _factor_summary(factors),
        "inference": score_alpha158(factors),
        "_note": "Alpha158 为 158 维截面特征，与 Alpha360 的 6×60 时序输入互补",
    }
    if include_all_factors:
        result["factors"] = factors
    else:
        result["highlights"] = {
            k: factors[k]
            for k in (
                "KMID",
                "ROC5",
                "ROC20",
                "MA5",
                "MA20",
                "MA60",
                "STD20",
                "CNTP20",
                "SUMD20",
                "CORR20",
                "RSV20",
                "RANK20",
            )
            if k in factors
        }
    return result


def get_alpha158_factors(
    client: EastMoneyClient,
    secid: str,
    *,
    period: str = "daily",
    adjust: str = "qfq",
    include_all_factors: bool = False,
) -> dict[str, Any]:
    bars = get_kline(client, secid, period=period, adjust=adjust, limit=120)
    built = build_alpha158_from_bars(bars, include_all_factors=include_all_factors)
    built["secid"] = secid
    built["period"] = period
    built["adjust"] = adjust
    return built


def get_alpha158_score(
    client: EastMoneyClient,
    secid: str,
    *,
    period: str = "daily",
    adjust: str = "qfq",
    include_all_factors: bool = False,
) -> dict[str, Any]:
    return get_alpha158_factors(
        client,
        secid,
        period=period,
        adjust=adjust,
        include_all_factors=include_all_factors,
    )
