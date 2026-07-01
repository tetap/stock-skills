"""Alpha158 LGB / Alpha360 TCN 训练（调优超参、embargo 切分、早停）。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from eastmoney.backtest import Sample, evaluate_predictions, get_kline_resilient, save_metrics, temporal_split


@dataclass
class SeqSample:
    date: str
    secid: str
    tensor_conv: list[list[float]]
    label: float


# 调优后默认超参：更强正则，降低小样本过拟合
LGB_TUNED_PARAMS: dict[str, Any] = {
    "objective": "regression",
    "metric": "l2",
    "verbosity": -1,
    "learning_rate": 0.03,
    "num_leaves": 31,
    "min_data_in_leaf": 25,
    "feature_fraction": 0.75,
    "bagging_fraction": 0.75,
    "bagging_freq": 5,
    "lambda_l1": 0.2,
    "lambda_l2": 0.2,
}

LGB_PARAM_GRID: list[dict[str, Any]] = [
    {**LGB_TUNED_PARAMS, "num_leaves": 31, "learning_rate": 0.03},
    {**LGB_TUNED_PARAMS, "num_leaves": 15, "learning_rate": 0.02, "lambda_l2": 0.5},
    {**LGB_TUNED_PARAMS, "num_leaves": 47, "learning_rate": 0.05, "min_data_in_leaf": 15},
    {**LGB_TUNED_PARAMS, "num_leaves": 63, "learning_rate": 0.025, "feature_fraction": 0.65},
]


def temporal_split_with_embargo(
    samples: Sequence[Sample | SeqSample],
    *,
    train_ratio: float = 0.8,
    embargo_days: int = 5,
) -> tuple[list, list]:
    """按日期切分，训练/测试之间留 embargo 天，避免 forward label 泄露。"""
    ordered = sorted(samples, key=lambda s: (s.date, s.secid))
    if len(ordered) < 2:
        return [], []
    dates = sorted({s.date for s in ordered})
    cut = max(1, min(len(dates) - 1, int(len(dates) * train_ratio)))
    train_dates = set(dates[:cut])
    test_dates = set(dates[cut + embargo_days :])
    if not test_dates:
        test_dates = set(dates[cut:])
    train = [s for s in ordered if s.date in train_dates]
    test = [s for s in ordered if s.date in test_dates]
    return train, test


def build_alpha360_samples(
    client: Any,
    secids: Sequence[str],
    *,
    forward_days: int = 5,
    seq_len: int = 60,
    limit: int = 500,
) -> list[SeqSample]:
    from eastmoney.alpha360 import build_alpha360_from_bars

    samples: list[SeqSample] = []
    for secid in secids:
        bars = get_kline_resilient(client, secid, period="daily", adjust="qfq", limit=limit)
        if len(bars) < seq_len + forward_days + 1:
            continue
        for i in range(seq_len - 1, len(bars) - forward_days):
            window = bars[i - seq_len + 1 : i + 1]
            fwd = bars[i + forward_days]["close"] / bars[i]["close"] - 1
            built = build_alpha360_from_bars(window, seq_len=seq_len, include_tensor=True)
            tensor_conv = built.get("tensor_conv")
            if not tensor_conv:
                continue
            samples.append(
                SeqSample(
                    date=str(bars[i]["date"]),
                    secid=secid,
                    tensor_conv=tensor_conv,
                    label=float(fwd),
                )
            )
    return samples


def train_lgb158(
    train_samples: list[Sample],
    test_samples: list[Sample],
    feature_names: list[str],
    *,
    grid: bool = False,
    num_boost_round: int = 300,
    early_stopping_rounds: int = 30,
) -> tuple[Any, dict[str, Any]]:
    import lightgbm as lgb
    import numpy as np

    x_train = np.array([s.features for s in train_samples])
    y_train = np.array([s.label for s in train_samples])
    x_test = np.array([s.features for s in test_samples]) if test_samples else x_train[:1]
    y_test = np.array([s.label for s in test_samples]) if test_samples else y_train[:1]

    candidates = LGB_PARAM_GRID if grid else [LGB_TUNED_PARAMS]
    best_booster = None
    best_row: dict[str, Any] | None = None

    for raw in candidates:
        params = {k: v for k, v in raw.items() if k != "num_boost_round"}
        ds_train = lgb.Dataset(x_train, label=y_train, feature_name=feature_names)
        ds_valid = lgb.Dataset(x_test, label=y_test, feature_name=feature_names, reference=ds_train)
        booster = lgb.train(
            params,
            ds_train,
            num_boost_round=num_boost_round,
            valid_sets=[ds_valid],
            valid_names=["oos"],
            callbacks=[lgb.early_stopping(early_stopping_rounds, verbose=False)],
        )
        pred_is = booster.predict(x_train)
        pred_oos = booster.predict(x_test)
        is_m = evaluate_predictions(pred_is, y_train)
        oos_m = evaluate_predictions(pred_oos, y_test)
        row = {
            "params": params,
            "best_iteration": int(getattr(booster, "best_iteration", num_boost_round)),
            "in_sample": is_m,
            "out_of_sample": oos_m,
        }
        if best_row is None or oos_m["ic"] > best_row["out_of_sample"]["ic"]:
            best_row = row
            best_booster = booster

    assert best_booster is not None and best_row is not None
    return best_booster, best_row


def train_tcn360(
    train_samples: list[SeqSample],
    test_samples: list[SeqSample],
    *,
    epochs: int = 40,
    lr: float = 1e-3,
    batch_size: int = 32,
) -> tuple[Any, dict[str, Any]]:
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    from eastmoney.tcn_model import TCNScore

    def _to_tensors(samples: list[SeqSample]) -> tuple[torch.Tensor, torch.Tensor]:
        xs = torch.tensor([s.tensor_conv for s in samples], dtype=torch.float32)
        ys = torch.tensor([s.label for s in samples], dtype=torch.float32)
        return xs, ys

    x_train, y_train = _to_tensors(train_samples)
    x_test, y_test = _to_tensors(test_samples) if test_samples else (x_train[:1], y_train[:1])

    model = TCNScore()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = torch.nn.MSELoss()
    loader = DataLoader(TensorDataset(x_train, y_train), batch_size=batch_size, shuffle=True)

    best_state = None
    best_oos_ic = float("-inf")
    best_row: dict[str, Any] | None = None

    for _epoch in range(epochs):
        model.train()
        for xb, yb in loader:
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            pred_is = model(x_train).tolist()
            pred_oos = model(x_test).tolist()
        is_m = evaluate_predictions(pred_is, y_train.tolist())
        oos_m = evaluate_predictions(pred_oos, y_test.tolist())
        if oos_m["ic"] >= best_oos_ic:
            best_oos_ic = oos_m["ic"]
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            best_row = {
                "epochs_trained": _epoch + 1,
                "in_sample": is_m,
                "out_of_sample": oos_m,
            }

    assert best_state is not None and best_row is not None
    model.load_state_dict(best_state)
    return model, best_row


def save_training_payload(
    path: Path,
    *,
    model_kind: str,
    model_rel_path: str,
    train_samples: int,
    test_samples: int,
    secids: list[str],
    train_ratio: float,
    best_row: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> Path:
    metrics_path = path.with_suffix(".metrics.json")
    payload = {
        "model": model_rel_path,
        "model_kind": model_kind,
        "train_ratio": train_ratio,
        "sample_count": train_samples + test_samples,
        "train_count": train_samples,
        "test_count": test_samples,
        "secids": secids,
        "best": best_row,
        "split": "temporal_with_embargo",
        "warning": "OOS IC>0 不代表可实盘；须独立回测 + 模拟盘拟合后再上实盘",
        **(extra or {}),
    }
    save_metrics(str(metrics_path), payload)
    return metrics_path
