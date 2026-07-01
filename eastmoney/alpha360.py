"""Alpha360 风格价量张量：6 通道 × 60 时间步，供 TCN/LSTM/Transformer 使用。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.kline import get_kline_resilient as get_kline

CHANNELS = ("open", "high", "low", "close", "vwap", "volume")
DEFAULT_SEQ_LEN = 60


def _vwap(bar: dict[str, Any]) -> float:
    volume = float(bar.get("volume") or 0)
    amount = float(bar.get("amount") or 0)
    if volume > 0 and amount > 0:
        return amount / volume
    high = float(bar["high"])
    low = float(bar["low"])
    close = float(bar["close"])
    return (high + low + close) / 3


def _linear_slope(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return num / den if den else 0.0


def build_alpha360_from_bars(
    bars: list[dict[str, Any]],
    *,
    seq_len: int = DEFAULT_SEQ_LEN,
    include_tensor: bool = True,
) -> dict[str, Any]:
    """由 K 线列表构造 Alpha360 张量（与 Qlib 列序一致）。

    - tensor_rnn: (seq_len, 6) — LSTM/Transformer，每步 [O,H,L,C,VWAP,Vol]
    - tensor_conv: (6, seq_len) — TCN，6 路 channel × 时间
    - flat_qlib: 长度 360，顺序 CLOSE→OPEN→HIGH→LOW→VWAP→VOLUME，各 60 点
    """
    if len(bars) < seq_len:
        raise ValueError(f"K 线不足 {seq_len} 根，当前 {len(bars)} 根")

    window = bars[-seq_len:]
    ref_close = float(window[-1]["close"])
    ref_volume = float(window[-1]["volume"])
    if ref_close <= 0:
        raise ValueError("最新收盘价无效")

    dates = [str(b["date"]) for b in window]
    tensor_rnn: list[list[float]] = []
    for bar in window:
        vwap = _vwap(bar)
        vol = float(bar["volume"])
        tensor_rnn.append(
            [
                float(bar["open"]) / ref_close,
                float(bar["high"]) / ref_close,
                float(bar["low"]) / ref_close,
                float(bar["close"]) / ref_close,
                vwap / ref_close,
                vol / (ref_volume + 1e-12),
            ]
        )

    tensor_conv = [
        [tensor_rnn[t][c] for t in range(seq_len)] for c in range(len(CHANNELS))
    ]

    flat_qlib: list[float] = []
    # 与 Qlib Alpha360 列序一致：CLOSE → OPEN → HIGH → LOW → VWAP → VOLUME
    for channel_idx in (3, 0, 1, 2, 4, 5):
        flat_qlib.extend(tensor_conv[channel_idx])

    close_series = [row[3] for row in tensor_rnn]
    volume_series = [row[5] for row in tensor_rnn]
    high_max = max(row[1] for row in tensor_rnn)
    low_min = min(row[2] for row in tensor_rnn)

    raw_closes = [float(b["close"]) for b in window]

    def _pct_change(days: int) -> float | None:
        if len(raw_closes) <= days:
            return None
        base = raw_closes[-1 - days]
        if base == 0:
            return None
        return round((raw_closes[-1] / base - 1) * 100, 2)

    early_close = sum(close_series[:5]) / 5
    late_close = sum(close_series[-5:]) / 5
    early_vol = sum(volume_series[:5]) / 5
    late_vol = sum(volume_series[-5:]) / 5

    slope_60 = _linear_slope(close_series)
    slope_5 = _linear_slope(close_series[-5:]) if len(close_series) >= 5 else slope_60
    slope_10 = _linear_slope(close_series[-10:]) if len(close_series) >= 10 else slope_60

    def _pattern(s: float) -> str:
        if s > 0.002:
            return "上升通道"
        if s < -0.002:
            return "下降通道"
        return "横盘震荡"

    pattern_60 = _pattern(slope_60)
    pattern_5 = _pattern(slope_5)

    result: dict[str, Any] = {
        "seq_len": seq_len,
        "input_size": len(CHANNELS),
        "channels": list(CHANNELS),
        "channel_order_note": "每步向量顺序 open, high, low, close, vwap, volume（均已归一化）",
        "dates": dates,
        "start_date": dates[0],
        "end_date": dates[-1],
        "ref_close": ref_close,
        "ref_volume": ref_volume,
        "normalization": {
            "price": "各 OHLC/VWAP ÷ 当日 close",
            "volume": "各 volume ÷ 当日 volume",
        },
        "layouts": {
            "rnn": {
                "shape": [seq_len, len(CHANNELS)],
                "usage": "LSTM / Transformer / TRA：input (batch, seq_len, input_size)",
            },
            "conv": {
                "shape": [len(CHANNELS), seq_len],
                "usage": "TCN：reshape 为 (batch, 6, 60) 后在时间维卷积",
            },
            "flat_qlib": {
                "shape": [len(CHANNELS) * seq_len],
                "usage": "仅存储兼容；时序模型请用 rnn/conv，勿当 360 个独立因子",
            },
        },
        "sequence_summary": {
            "pattern": pattern_60,
            "pattern_5d": pattern_5,
            "pattern_60d": pattern_60,
            "close_slope_norm": round(slope_60, 6),
            "close_slope_5d": round(slope_5, 6),
            "close_slope_10d": round(slope_10, 6),
            "close_change_5d_pct": _pct_change(5),
            "close_change_10d_pct": _pct_change(10),
            "close_change_20d_pct": _pct_change(20),
            "close_change_early_vs_late_pct": round((late_close / early_close - 1) * 100, 2)
            if early_close
            else None,
            "volume_ratio_late_early": round(late_vol / early_vol, 3) if early_vol else None,
            "high_vs_ref_close_pct": round((high_max - 1) * 100, 2),
            "low_vs_ref_close_pct": round((low_min - 1) * 100, 2),
            "latest_close_norm": round(close_series[-1], 6),
        },
        "_note": "Alpha360 为 6×60 时序输入，非 360 维表格因子",
    }

    if include_tensor:
        result["tensor_rnn"] = tensor_rnn
        result["tensor_conv"] = tensor_conv
        result["flat_qlib"] = flat_qlib

    return result


def get_alpha360_tensor(
    client: EastMoneyClient,
    secid: str,
    *,
    seq_len: int = DEFAULT_SEQ_LEN,
    period: str = "daily",
    adjust: str = "qfq",
    include_tensor: bool = False,
) -> dict[str, Any]:
    """拉取 K 线并构造 Alpha360 张量。默认仅返回摘要，避免 JSON 过大。"""
    need = max(seq_len + 5, seq_len)
    bars = get_kline(client, secid, period=period, adjust=adjust, limit=need)
    built = build_alpha360_from_bars(bars, seq_len=seq_len, include_tensor=include_tensor)
    built["secid"] = secid
    built["period"] = period
    built["adjust"] = adjust
    return built
