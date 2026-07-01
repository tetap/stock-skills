#!/usr/bin/env python3
"""Alpha158 启发式/模型分数 → 简易 long-only 回测 + 阈值网格（样本内搜参、样本外验证）。

用法:
  python scripts/backtest_quant.py --secid 0.300204 --limit 500
  python scripts/backtest_quant.py --secid 0.002074 --grid-thresholds
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _heuristic_scores(client, secid: str, limit: int) -> tuple[list[str], list[float], list[float]]:
    from eastmoney.alpha158 import _bars_to_frame, compute_alpha158_from_frame, score_alpha158_heuristic
    from eastmoney.kline import get_kline

    bars = get_kline(client, secid, period="daily", adjust="qfq", limit=limit)
    dates: list[str] = []
    scores: list[float] = []
    fwd_returns: list[float] = []

    for i in range(60, len(bars) - 5):
        window = bars[: i + 1]
        factors = compute_alpha158_from_frame(_bars_to_frame(window))
        inf = score_alpha158_heuristic(factors)
        dates.append(str(bars[i]["date"]))
        scores.append(float(inf["score"]))
        fwd_returns.append(bars[i + 5]["close"] / bars[i]["close"] - 1)

    return dates, scores, fwd_returns


def main() -> None:
    p = argparse.ArgumentParser(description="量化信号简易回测（80/20 时序切分）")
    p.add_argument("--secid", default="0.300204")
    p.add_argument("--limit", type=int, default=500)
    p.add_argument("--train-ratio", type=float, default=0.8)
    p.add_argument("--grid-thresholds", action="store_true", help="样本内网格搜索做多阈值")
    p.add_argument("--long-threshold", type=float, default=20.0)
    p.add_argument("--fee", type=float, default=0.001, help="单边换手费率")
    p.add_argument("--out", default="", help="结果 JSON 路径")
    args = p.parse_args()

    from eastmoney.backtest import grid_search_thresholds, run_long_only_backtest, score_to_signal
    from eastmoney.client import EastMoneyClient

    client = EastMoneyClient()
    dates, scores, fwd = _heuristic_scores(client, args.secid, args.limit)
    if len(scores) < 40:
        raise SystemExit(f"样本不足: {len(scores)}")

    cut = max(1, min(len(scores) - 1, int(len(scores) * args.train_ratio)))
    is_scores, is_fwd = scores[:cut], fwd[:cut]
    oos_scores, oos_fwd = scores[cut:], fwd[cut:]

    if args.grid_thresholds:
        grid = grid_search_thresholds(is_scores, is_fwd)
        best_th = grid["best"]["long_threshold"]
        oos_positions = [max(0, score_to_signal(s, long_threshold=best_th)) for s in oos_scores]
        oos_stats = run_long_only_backtest(oos_fwd, oos_positions, fee_rate=args.fee)
        payload = {
            "secid": args.secid,
            "method": "alpha158_heuristic_long_only",
            "in_sample_grid": grid,
            "out_of_sample": oos_stats,
            "note": "样本内选阈值 → 样本外验证；与 TradingView 结果须人工交叉核对",
        }
    else:
        positions = [max(0, score_to_signal(s, long_threshold=args.long_threshold)) for s in scores]
        payload = {
            "secid": args.secid,
            "long_threshold": args.long_threshold,
            "full_sample": run_long_only_backtest(fwd, positions, fee_rate=args.fee),
            "in_sample": run_long_only_backtest(is_fwd, positions[:cut], fee_rate=args.fee),
            "out_of_sample": run_long_only_backtest(oos_fwd, positions[cut:], fee_rate=args.fee),
        }

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
