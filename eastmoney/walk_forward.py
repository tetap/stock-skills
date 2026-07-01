"""Walk-forward 回测：滚动样本外 fold + 阈值网格。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from eastmoney.backtest import grid_search_thresholds, run_long_only_backtest, score_to_signal


@dataclass
class SignalSeries:
    dates: list[str]
    scores: list[float]
    forward_returns: list[float]
    method: str


def walk_forward_fold_ranges(
    n: int,
    *,
    n_folds: int = 5,
    min_train: int = 60,
) -> list[tuple[range, range]]:
    """将 [min_train, n) 划分为 n_folds 个 OOS 窗口；每 fold 训练集为 expanding window。"""
    if n <= min_train + 5:
        return []
    oos_start = min_train
    oos_total = n - oos_start
    fold_size = max(5, oos_total // n_folds)
    folds: list[tuple[range, range]] = []
    for i in range(n_folds):
        test_start = oos_start + i * fold_size
        test_end = min(n, test_start + fold_size) if i < n_folds - 1 else n
        if test_start >= n or test_end - test_start < 3:
            break
        folds.append((range(0, test_start), range(test_start, test_end)))
    return folds


def run_walk_forward_backtest(
    series: SignalSeries,
    *,
    n_folds: int = 5,
    min_train: int = 60,
    fee_rate: float = 0.001,
    long_grid: Sequence[float] = (15, 20, 25, 30),
) -> dict[str, Any]:
    """每 fold：样本内网格搜 long_threshold → 样本外 long-only 回测。"""
    n = len(series.scores)
    folds = walk_forward_fold_ranges(n, n_folds=n_folds, min_train=min_train)
    if not folds:
        raise ValueError(f"样本不足 walk-forward: n={n}, min_train={min_train}")

    fold_rows: list[dict[str, Any]] = []
    oos_returns: list[float] = []
    oos_positions: list[int] = []

    for idx, (train_rng, test_rng) in enumerate(folds, start=1):
        tr_scores = [series.scores[i] for i in train_rng]
        tr_fwd = [series.forward_returns[i] for i in train_rng]
        te_scores = [series.scores[i] for i in test_rng]
        te_fwd = [series.forward_returns[i] for i in test_rng]

        grid = grid_search_thresholds(tr_scores, tr_fwd, long_grid=long_grid)
        best_th = float(grid["best"]["long_threshold"])
        positions = [max(0, score_to_signal(s, long_threshold=best_th)) for s in te_scores]
        stats = run_long_only_backtest(te_fwd, positions, fee_rate=fee_rate)

        fold_rows.append(
            {
                "fold": idx,
                "train_size": len(tr_scores),
                "test_size": len(te_scores),
                "test_dates": [series.dates[i] for i in test_rng],
                "best_long_threshold": best_th,
                "in_sample_grid": grid,
                "out_of_sample": stats,
            }
        )
        oos_returns.extend(te_fwd)
        oos_positions.extend(positions)

    combined = run_long_only_backtest(oos_returns, oos_positions, fee_rate=fee_rate)
    return {
        "method": series.method,
        "n_folds": len(fold_rows),
        "min_train": min_train,
        "folds": fold_rows,
        "combined_out_of_sample": combined,
        "note": "每 fold IS 搜阈值 → OOS 验证；combined 为各 fold OOS 拼接",
    }
