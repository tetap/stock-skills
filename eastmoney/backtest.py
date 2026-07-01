"""量化回测与样本内外评估（对齐「80% 挖因子 + 20% 验证 + 网格搜参」思路）。"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Callable, Sequence


@dataclass
class Sample:
    date: str
    secid: str
    features: list[float]
    label: float  # forward return


def temporal_split(samples: Sequence[Sample], train_ratio: float = 0.8) -> tuple[list[Sample], list[Sample]]:
    """按时间排序后切分，避免未来信息泄露。"""
    ordered = sorted(samples, key=lambda s: (s.date, s.secid))
    if not ordered:
        return [], []
    cut = max(1, min(len(ordered) - 1, int(len(ordered) * train_ratio)))
    return list(ordered[:cut]), list(ordered[cut:])


def _rank(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def spearman_ic(preds: Sequence[float], labels: Sequence[float]) -> float:
    if len(preds) < 3:
        return 0.0
    rp = _rank(list(preds))
    rl = _rank(list(labels))
    n = len(preds)
    mp = sum(rp) / n
    ml = sum(rl) / n
    num = sum((a - mp) * (b - ml) for a, b in zip(rp, rl))
    den_p = math.sqrt(sum((a - mp) ** 2 for a in rp))
    den_l = math.sqrt(sum((b - ml) ** 2 for b in rl))
    if den_p == 0 or den_l == 0:
        return 0.0
    return num / (den_p * den_l)


def evaluate_predictions(preds: Sequence[float], labels: Sequence[float]) -> dict[str, float]:
    n = len(preds)
    if n == 0:
        return {"count": 0, "ic": 0.0, "rmse": 0.0, "direction_accuracy": 0.0}
    rmse = math.sqrt(sum((p - y) ** 2 for p, y in zip(preds, labels)) / n)
    dir_acc = sum(1 for p, y in zip(preds, labels) if p * y > 0 or (p == 0 and y == 0)) / n
    return {
        "count": float(n),
        "ic": round(spearman_ic(preds, labels), 4),
        "rmse": round(rmse, 6),
        "direction_accuracy": round(dir_acc, 4),
    }


def score_to_signal(score: float, *, long_threshold: float = 20.0, short_threshold: float = -20.0) -> int:
    """1=多, 0=空仓, -1=空（A 股现货回测通常只用 1/0）。"""
    if score >= long_threshold:
        return 1
    if score <= short_threshold:
        return -1
    return 0


def run_long_only_backtest(
    daily_returns: Sequence[float],
    positions: Sequence[int],
    *,
    fee_rate: float = 0.001,
) -> dict[str, Any]:
    """positions[i] 表示第 i 日收盘后持仓（0/1），收益来自下一日 daily_returns[i]。"""
    if len(daily_returns) != len(positions):
        raise ValueError("daily_returns 与 positions 长度须一致")
    equity = 1.0
    curve: list[float] = [equity]
    trades = 0
    prev = 0
    strat_returns: list[float] = []

    for i, ret in enumerate(daily_returns):
        pos = 1 if positions[i] > 0 else 0
        if pos != prev:
            equity *= 1.0 - fee_rate
            trades += 1
        prev = pos
        step = pos * ret
        strat_returns.append(step)
        equity *= 1.0 + step
        curve.append(equity)

    peak = curve[0]
    max_dd = 0.0
    for v in curve:
        peak = max(peak, v)
        max_dd = max(max_dd, (peak - v) / peak if peak else 0.0)

    mean_r = sum(strat_returns) / len(strat_returns) if strat_returns else 0.0
    var_r = sum((r - mean_r) ** 2 for r in strat_returns) / len(strat_returns) if strat_returns else 0.0
    sharpe = (mean_r / math.sqrt(var_r) * math.sqrt(252)) if var_r > 0 else 0.0

    return {
        "total_return": round(equity - 1.0, 4),
        "max_drawdown": round(max_dd, 4),
        "sharpe": round(sharpe, 3),
        "trades": trades,
        "days": len(daily_returns),
    }


def grid_search_thresholds(
    scores: Sequence[float],
    forward_returns: Sequence[float],
    *,
    long_grid: Sequence[float] = (15, 20, 25, 30),
    metric: str = "sharpe",
) -> dict[str, Any]:
    """在样本内网格搜索做多阈值（参数勿凭感觉设）。"""
    best: dict[str, Any] | None = None
    results: list[dict[str, Any]] = []

    daily_ret = list(forward_returns)
    for th in long_grid:
        positions = [score_to_signal(s, long_threshold=th) for s in scores]
        # 只做多：负信号当空仓
        positions = [max(0, p) for p in positions]
        stats = run_long_only_backtest(daily_ret, positions)
        row = {"long_threshold": th, **stats}
        results.append(row)
        if best is None or stats.get(metric, float("-inf")) > best.get(metric, float("-inf")):
            best = row

    return {"best": best, "grid": results, "metric": metric}


def get_kline_resilient(
    client: Any,
    secid: str,
    *,
    period: str = "daily",
    adjust: str = "qfq",
    limit: int = 120,
) -> list[dict[str, Any]]:
    """K 线：东财直连失败时降级 AkShare（训练/回测用）。"""
    from eastmoney.kline import get_kline_resilient as _resilient

    return _resilient(client, secid, period=period, adjust=adjust, limit=limit)


def build_alpha158_samples(
    client: Any,
    secids: Sequence[str],
    *,
    forward_days: int = 5,
    limit: int = 500,
) -> tuple[list[Sample], list[str]]:
    """从 K 线构建 Alpha158 监督样本（带 date/secid，供时序切分）。"""
    from eastmoney.alpha158 import _bars_to_frame, compute_alpha158_from_frame
    from eastmoney.ml_models import alpha158_feature_names

    samples: list[Sample] = []
    feature_names: list[str] = []

    for secid in secids:
        bars = get_kline_resilient(client, secid, period="daily", adjust="qfq", limit=limit)
        if len(bars) < 80:
            continue
        for i in range(60, len(bars) - forward_days):
            window = bars[: i + 1]
            fwd = bars[i + forward_days]["close"] / bars[i]["close"] - 1
            factors = compute_alpha158_from_frame(_bars_to_frame(window))
            if not feature_names:
                feature_names = alpha158_feature_names(factors)
            vec = [float(factors.get(k) or 0) for k in feature_names]
            samples.append(
                Sample(
                    date=str(bars[i]["date"]),
                    secid=secid,
                    features=vec,
                    label=float(fwd),
                )
            )
    return samples, feature_names


def save_metrics(path: str, payload: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
