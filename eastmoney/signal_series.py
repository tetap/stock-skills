"""Alpha158 信号序列（启发式 / LightGBM）。"""

from __future__ import annotations

from typing import Any

from eastmoney.walk_forward import SignalSeries


def build_heuristic_signal_series(
    client: Any,
    secid: str,
    *,
    limit: int = 500,
    forward_days: int = 5,
) -> SignalSeries:
    from eastmoney.alpha158 import _bars_to_frame, compute_alpha158_from_frame, score_alpha158_heuristic
    from eastmoney.backtest import get_kline_resilient

    bars = get_kline_resilient(client, secid, period="daily", adjust="qfq", limit=limit)
    dates: list[str] = []
    scores: list[float] = []
    fwd_returns: list[float] = []

    for i in range(60, len(bars) - forward_days):
        window = bars[: i + 1]
        factors = compute_alpha158_from_frame(_bars_to_frame(window))
        inf = score_alpha158_heuristic(factors)
        dates.append(str(bars[i]["date"]))
        scores.append(float(inf["score"]))
        fwd_returns.append(bars[i + forward_days]["close"] / bars[i]["close"] - 1)

    return SignalSeries(dates=dates, scores=scores, forward_returns=fwd_returns, method="alpha158_heuristic")


def build_lgb_signal_series(
    client: Any,
    secid: str,
    *,
    limit: int = 500,
    forward_days: int = 5,
    model_path: str | None = None,
) -> SignalSeries | None:
    from eastmoney.alpha158 import _bars_to_frame, compute_alpha158_from_frame
    from eastmoney.backtest import get_kline_resilient
    from eastmoney.ml_models import try_lgb158_score

    probe = try_lgb158_score({"ROC5": 0.0}, model_path=model_path)
    if probe is None:
        return None

    bars = get_kline_resilient(client, secid, period="daily", adjust="qfq", limit=limit)
    dates: list[str] = []
    scores: list[float] = []
    fwd_returns: list[float] = []

    for i in range(60, len(bars) - forward_days):
        window = bars[: i + 1]
        factors = compute_alpha158_from_frame(_bars_to_frame(window))
        inf = try_lgb158_score(factors, model_path=model_path)
        if not inf:
            return None
        dates.append(str(bars[i]["date"]))
        scores.append(float(inf["score"]))
        fwd_returns.append(bars[i + forward_days]["close"] / bars[i]["close"] - 1)

    return SignalSeries(dates=dates, scores=scores, forward_returns=fwd_returns, method="alpha158_lightgbm")
