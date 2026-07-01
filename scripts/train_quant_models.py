#!/usr/bin/env python3
"""训练/初始化量化模型（Alpha158 LGB 调优 · Alpha360 TCN · GluonTS DeepAR）。

用法:
  python scripts/train_quant_models.py --lgb
  python scripts/train_quant_models.py --lgb --grid
  python scripts/train_quant_models.py --tcn
  python scripts/train_quant_models.py --deepar
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


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def run_lgb(
    secids: list[str],
    *,
    out: Path,
    train_ratio: float,
    limit: int,
    grid: bool,
    embargo_days: int,
) -> None:
    from eastmoney.backtest import build_alpha158_samples
    from eastmoney.client import EastMoneyClient
    from eastmoney.ml_models import evaluate_oos_metrics
    from eastmoney.quant_training import (
        save_training_payload,
        temporal_split_with_embargo,
        train_lgb158,
    )

    client = EastMoneyClient(min_interval=1.0, max_retries=4)
    samples, feature_names = build_alpha158_samples(client, secids, forward_days=5, limit=limit)
    if len(samples) < 80:
        raise SystemExit(f"样本不足 ({len(samples)} 条)，请增加 --secids 或 --limit")

    train_samples, test_samples = temporal_split_with_embargo(
        samples, train_ratio=train_ratio, embargo_days=embargo_days
    )
    if len(test_samples) < 10:
        raise SystemExit("OOS 样本过少，请增加 limit 或降低 train_ratio")

    booster, best_row = train_lgb158(
        train_samples, test_samples, feature_names, grid=grid
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    booster.save_model(str(out))

    metrics_path = save_training_payload(
        out,
        model_kind="alpha158_lightgbm",
        model_rel_path=_repo_relative(out),
        train_samples=len(train_samples),
        test_samples=len(test_samples),
        secids=secids,
        train_ratio=train_ratio,
        best_row=best_row,
        extra={"grid_searched": grid, "embargo_days": embargo_days, "tuned": True},
    )

    gate = evaluate_oos_metrics(best_row["out_of_sample"])
    print(f"LightGBM 已保存: {out}")
    print(f"样本: 总 {len(samples)} | 内 {len(train_samples)} | 外 {len(test_samples)} | embargo {embargo_days}d")
    print(f"IS  IC={best_row['in_sample']['ic']}  dir_acc={best_row['in_sample']['direction_accuracy']}")
    print(f"OOS IC={best_row['out_of_sample']['ic']}  dir_acc={best_row['out_of_sample']['direction_accuracy']}")
    print(f"best_iteration={best_row.get('best_iteration')}")
    print(f"指标 JSON: {metrics_path}")
    print(gate["summary"])
    if not gate["passed"]:
        print("⚠ 该模型尚未通过样本外检验，勿用于报告定调。")


def run_tcn(
    secids: list[str],
    *,
    out: Path,
    train_ratio: float,
    limit: int,
    embargo_days: int,
    epochs: int,
) -> None:
    import torch

    from eastmoney.client import EastMoneyClient
    from eastmoney.ml_models import evaluate_oos_metrics
    from eastmoney.quant_training import (
        build_alpha360_samples,
        save_training_payload,
        temporal_split_with_embargo,
        train_tcn360,
    )

    client = EastMoneyClient(min_interval=1.0, max_retries=4)
    samples = build_alpha360_samples(client, secids, forward_days=5, limit=limit)
    if len(samples) < 60:
        raise SystemExit(f"Alpha360 样本不足 ({len(samples)})")

    train_samples, test_samples = temporal_split_with_embargo(
        samples, train_ratio=train_ratio, embargo_days=embargo_days
    )
    model, best_row = train_tcn360(train_samples, test_samples, epochs=epochs)
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out)

    metrics_path = save_training_payload(
        out,
        model_kind="alpha360_tcn",
        model_rel_path=_repo_relative(out),
        train_samples=len(train_samples),
        test_samples=len(test_samples),
        secids=secids,
        train_ratio=train_ratio,
        best_row=best_row,
        extra={"embargo_days": embargo_days, "epochs": epochs},
    )

    gate = evaluate_oos_metrics(best_row["out_of_sample"])
    print(f"TCN 已保存: {out}")
    print(f"OOS IC={best_row['out_of_sample']['ic']}  dir_acc={best_row['out_of_sample']['direction_accuracy']}")
    print(f"指标 JSON: {metrics_path}")
    print(gate["summary"])


def run_deepar(
    secids: list[str],
    *,
    limit: int,
    train_ratio: float,
    max_epochs: int,
) -> None:
    from eastmoney.client import EastMoneyClient
    from eastmoney.gluonts_adapter import train_deepar

    client = EastMoneyClient(min_interval=1.0, max_retries=4)
    meta = train_deepar(
        client,
        secids,
        limit=limit,
        train_ratio=train_ratio,
        max_epochs=max_epochs,
    )
    print(f"GluonTS DeepAR 已保存: {meta['model_dir']}")
    print(f"OOS: {meta.get('oos_passed')}  series={meta.get('series_count')}")
    print(f"metrics: {meta['model_dir']}/metrics.json")


def run_tft(
    secids: list[str],
    *,
    limit: int,
    train_ratio: float,
    max_epochs: int,
) -> None:
    from eastmoney.client import EastMoneyClient
    from eastmoney.gluonts_adapter import train_tft

    client = EastMoneyClient(min_interval=1.0, max_retries=4)
    meta = train_tft(
        client,
        secids,
        limit=limit,
        train_ratio=train_ratio,
        max_epochs=max_epochs,
    )
    print(f"GluonTS TFT 已保存: {meta['model_dir']}")
    print(f"OOS: {meta.get('oos_passed')}  series={meta.get('series_count')}")
    print(f"metrics: {meta['model_dir']}/metrics.json")


def init_tcn(out: Path) -> None:
    import torch

    from eastmoney.tcn_model import TCNScore

    model = TCNScore()
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out)
    print(f"TCN 占位权重已保存: {out}")
    print("注意: 随机初始化；请使用 --tcn 进行真实训练。")


def main() -> None:
    p = argparse.ArgumentParser(description="训练 Alpha158 LGB / Alpha360 TCN / GluonTS DeepAR·TFT")
    p.add_argument("--lgb", action="store_true", help="调优 LightGBM → models/alpha158_lgb.txt")
    p.add_argument("--tcn", action="store_true", help="训练 Alpha360 TCN → models/alpha360_tcn.pt")
    p.add_argument("--deepar", action="store_true", help="GluonTS DeepAR → models/gluonts_deepar/")
    p.add_argument("--tft", action="store_true", help="GluonTS TFT → models/gluonts_tft/")
    p.add_argument("--tcn-init", action="store_true", help="导出 TCN 随机初始化")
    p.add_argument("--secids", default=",".join(DEFAULT_SECIDS))
    p.add_argument("--limit", type=int, default=500)
    p.add_argument("--train-ratio", type=float, default=0.8)
    p.add_argument("--embargo-days", type=int, default=5, help="训练/测试间 embargo（与 forward_days 对齐）")
    p.add_argument("--grid", action="store_true", help="LGB 网格搜参（OOS IC 选优）")
    p.add_argument("--epochs", type=int, default=40, help="TCN 训练轮数")
    p.add_argument("--deepar-epochs", type=int, default=15)
    p.add_argument("--tft-epochs", type=int, default=10)
    p.add_argument("--lgb-out", default=str(MODEL_DIR / "alpha158_lgb.txt"))
    p.add_argument("--tcn-out", default=str(MODEL_DIR / "alpha360_tcn.pt"))
    args = p.parse_args()

    if not any([args.lgb, args.tcn, args.deepar, args.tft, args.tcn_init]):
        p.print_help()
        raise SystemExit(0)

    secids = [s.strip() for s in args.secids.split(",") if s.strip()]

    if args.lgb:
        run_lgb(
            secids,
            out=Path(args.lgb_out),
            train_ratio=args.train_ratio,
            limit=args.limit,
            grid=args.grid,
            embargo_days=args.embargo_days,
        )
    if args.tcn:
        run_tcn(
            secids,
            out=Path(args.tcn_out),
            train_ratio=args.train_ratio,
            limit=args.limit,
            embargo_days=args.embargo_days,
            epochs=args.epochs,
        )
    if args.deepar:
        run_deepar(secids, limit=args.limit, train_ratio=args.train_ratio, max_epochs=args.deepar_epochs)
    if args.tft:
        run_tft(secids, limit=args.limit, train_ratio=args.train_ratio, max_epochs=args.tft_epochs)
    if args.tcn_init:
        init_tcn(Path(args.tcn_out))


if __name__ == "__main__":
    main()
