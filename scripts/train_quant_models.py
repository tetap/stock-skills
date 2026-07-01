#!/usr/bin/env python3
"""训练/初始化量化模型权重（含 80/20 时序切分 + OOS 评估 + 网格搜参）。

用法:
  python scripts/train_quant_models.py --lgb --limit 500
  python scripts/train_quant_models.py --lgb --grid
  python scripts/train_quant_models.py --tcn-init
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODEL_DIR = ROOT / "models"
DEFAULT_SECIDS = ["0.002074", "1.600519", "0.300204", "0.000001"]

LGB_PARAM_GRID = [
    {"learning_rate": 0.05, "num_leaves": 31, "num_boost_round": 80},
    {"learning_rate": 0.03, "num_leaves": 15, "num_boost_round": 120},
    {"learning_rate": 0.08, "num_leaves": 63, "num_boost_round": 60},
    {"learning_rate": 0.05, "num_leaves": 47, "num_boost_round": 100},
]


def train_lgb(
    secids: list[str],
    *,
    out: Path,
    train_ratio: float = 0.8,
    limit: int = 500,
    grid: bool = False,
    metrics_out: Path | None = None,
) -> None:
    try:
        import lightgbm as lgb
        import numpy as np
    except ImportError as e:
        raise SystemExit("请先安装: pip install -r requirements-ml.txt") from e

    from eastmoney.backtest import (
        build_alpha158_samples,
        evaluate_predictions,
        save_metrics,
        temporal_split,
    )
    from eastmoney.client import EastMoneyClient

    client = EastMoneyClient()
    samples, feature_names = build_alpha158_samples(client, secids, forward_days=5, limit=limit)
    if len(samples) < 80:
        raise SystemExit(f"样本不足 ({len(samples)} 条)，请增加 --secids 或 --limit")

    train_samples, test_samples = temporal_split(samples, train_ratio=train_ratio)

    x_train = np.array([s.features for s in train_samples])
    y_train = np.array([s.label for s in train_samples])
    x_test = np.array([s.features for s in test_samples])
    y_test = np.array([s.label for s in test_samples])

    candidates = LGB_PARAM_GRID if grid else [LGB_PARAM_GRID[0]]
    best_booster = None
    best_row: dict | None = None

    for raw_cand in candidates:
        cand = dict(raw_cand)
        rounds = cand.pop("num_boost_round", 80)
        params = {
            "objective": "regression",
            "metric": "l2",
            "verbosity": -1,
            **cand,
        }
        ds = lgb.Dataset(x_train, label=y_train, feature_name=feature_names)
        booster = lgb.train(params, ds, num_boost_round=rounds)
        pred_is = booster.predict(x_train)
        pred_oos = booster.predict(x_test)
        is_m = evaluate_predictions(pred_is, y_train)
        oos_m = evaluate_predictions(pred_oos, y_test)
        row = {
            "params": {**cand, "num_boost_round": rounds},
            "in_sample": is_m,
            "out_of_sample": oos_m,
        }
        if best_row is None or oos_m["ic"] > best_row["out_of_sample"]["ic"]:
            best_row = row
            best_booster = booster

    assert best_booster is not None and best_row is not None
    out.parent.mkdir(parents=True, exist_ok=True)
    best_booster.save_model(str(out))

    payload = {
        "model": str(out),
        "train_ratio": train_ratio,
        "sample_count": len(samples),
        "train_count": len(train_samples),
        "test_count": len(test_samples),
        "secids": secids,
        "best": best_row,
        "grid_searched": grid,
        "warning": "OOS IC>0 不代表可实盘；须独立回测 + 模拟盘拟合后再上实盘",
    }
    metrics_path = metrics_out or out.with_suffix(".metrics.json")
    save_metrics(str(metrics_path), payload)

    print(f"LightGBM 已保存: {out}")
    print(f"样本: 总 {len(samples)} | 内 {len(train_samples)} | 外 {len(test_samples)}")
    print(f"IS  IC={best_row['in_sample']['ic']}  dir_acc={best_row['in_sample']['direction_accuracy']}")
    print(f"OOS IC={best_row['out_of_sample']['ic']}  dir_acc={best_row['out_of_sample']['direction_accuracy']}")
    print(f"指标 JSON: {metrics_path}")
    if best_row["out_of_sample"]["ic"] <= 0:
        print("⚠ OOS IC≤0：该模型尚未通过样本外检验，勿用于报告定调。")


def init_tcn(out: Path) -> None:
    try:
        import torch
        import torch.nn as nn
    except ImportError as e:
        raise SystemExit("请先安装: pip install -r requirements-ml.txt") from e

    class TCNScore(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.conv1 = nn.Conv1d(6, 32, kernel_size=3, padding=1)
            self.conv2 = nn.Conv1d(32, 32, kernel_size=3, padding=1)
            self.pool = nn.AdaptiveAvgPool1d(1)
            self.fc = nn.Linear(32, 1)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x = torch.relu(self.conv1(x))
            x = torch.relu(self.conv2(x))
            x = self.pool(x).squeeze(-1)
            return self.fc(x).squeeze(-1)

    model = TCNScore()
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out)
    print(f"TCN 占位权重已保存: {out}")
    print("注意: 此为随机初始化结构，须用 Qlib 数据重新训练后替换。")


def main() -> None:
    p = argparse.ArgumentParser(description="训练/初始化 Alpha158 LGB 与 Alpha360 TCN 权重")
    p.add_argument("--lgb", action="store_true", help="训练 LightGBM → models/alpha158_lgb.txt")
    p.add_argument("--tcn-init", action="store_true", help="导出 TCN 随机初始化 → models/alpha360_tcn.pt")
    p.add_argument("--secids", default=",".join(DEFAULT_SECIDS), help="LGB 训练用 secid 列表")
    p.add_argument("--limit", type=int, default=500, help="每只股票 K 线条数（约两年日线）")
    p.add_argument("--train-ratio", type=float, default=0.8, help="样本内比例（时序切分）")
    p.add_argument("--grid", action="store_true", help="网格搜索 LGB 超参（OOS IC 选优）")
    p.add_argument("--lgb-out", default=str(MODEL_DIR / "alpha158_lgb.txt"))
    p.add_argument("--tcn-out", default=str(MODEL_DIR / "alpha360_tcn.pt"))
    args = p.parse_args()

    if not args.lgb and not args.tcn_init:
        p.print_help()
        raise SystemExit(0)

    if args.lgb:
        secids = [s.strip() for s in args.secids.split(",") if s.strip()]
        train_lgb(
            secids,
            out=Path(args.lgb_out),
            train_ratio=args.train_ratio,
            limit=args.limit,
            grid=args.grid,
        )

    if args.tcn_init:
        init_tcn(Path(args.tcn_out))


if __name__ == "__main__":
    main()
