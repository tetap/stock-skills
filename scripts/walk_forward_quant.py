#!/usr/bin/env python3
"""Walk-forward 量化回测（滚动 OOS fold + 阈值网格）。

用法:
  python scripts/walk_forward_quant.py --secid 0.300204
  python scripts/walk_forward_quant.py --secid 1.600519 --method lgb --folds 5
  python scripts/walk_forward_quant.py --secid 0.002594 --method heuristic --out results/wf.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    p = argparse.ArgumentParser(description="Walk-forward long-only 回测")
    p.add_argument("--secid", required=True)
    p.add_argument("--limit", type=int, default=500)
    p.add_argument("--method", choices=("heuristic", "lgb", "auto"), default="auto")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--min-train", type=int, default=60)
    p.add_argument("--fee", type=float, default=0.001)
    p.add_argument("--lgb-path", default="", help="自定义 LGB 权重路径")
    p.add_argument("--out", default="", help="JSON 输出路径")
    args = p.parse_args()

    from eastmoney.client import EastMoneyClient
    from eastmoney.signal_series import build_heuristic_signal_series, build_lgb_signal_series
    from eastmoney.walk_forward import run_walk_forward_backtest

    client = EastMoneyClient(min_interval=0.8, max_retries=3)
    model_path = args.lgb_path or None

    series = None
    if args.method in ("lgb", "auto"):
        series = build_lgb_signal_series(client, args.secid, limit=args.limit, model_path=model_path)
    if series is None:
        if args.method == "lgb":
            raise SystemExit("LGB 权重不可用，请先 train_quant_models.py --lgb")
        series = build_heuristic_signal_series(client, args.secid, limit=args.limit)

    if len(series.scores) < args.min_train + 15:
        raise SystemExit(f"样本不足: {len(series.scores)}")

    payload = run_walk_forward_backtest(
        series,
        n_folds=args.folds,
        min_train=args.min_train,
        fee_rate=args.fee,
    )
    payload["secid"] = args.secid
    payload["limit"] = args.limit

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
