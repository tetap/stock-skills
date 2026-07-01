"""Alpha360 序列打分：启发式特征 + 可选 PyTorch TCN 推理。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from eastmoney.alpha360 import build_alpha360_from_bars, get_alpha360_tensor
from eastmoney.client import EastMoneyClient

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "alpha360_tcn.pt"


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def score_alpha360_heuristic(built: dict[str, Any]) -> dict[str, Any]:
    """基于 6×60 张量的序列特征打分（非 Qlib 预训练权重）。"""
    summary = built.get("sequence_summary") or {}
    tensor_rnn = built.get("tensor_rnn")

    slope = float(summary.get("close_slope_norm") or 0)
    early_late = float(summary.get("close_change_early_vs_late_pct") or 0)
    vol_ratio = float(summary.get("volume_ratio_late_early") or 1)
    high_pct = float(summary.get("high_vs_ref_close_pct") or 0)
    low_pct = float(summary.get("low_vs_ref_close_pct") or 0)

    trend = _clamp(slope * 8000, -35, 35)
    momentum = _clamp(early_late * 1.5, -30, 30)
    vol_confirm = _clamp((vol_ratio - 1) * 15, -15, 15)
    if trend * vol_confirm < 0:
        vol_confirm *= 0.3

    range_pct = high_pct - low_pct
    position = 0.0
    if tensor_rnn and range_pct > 0.1:
        close_series = [row[3] for row in tensor_rnn]
        pos_in_range = (close_series[-1] - (1 + low_pct / 100)) / (range_pct / 100 + 1e-9)
        position = _clamp((pos_in_range - 0.5) * 20, -15, 15)

    raw = trend + momentum + vol_confirm + position
    score = round(_clamp(raw, -100, 100), 2)

    if score >= 25:
        verdict = "序列偏多"
    elif score <= -25:
        verdict = "序列偏空"
    else:
        verdict = "序列中性"

    signals = sum(
        1
        for x in (trend, momentum, vol_confirm if trend >= 0 else -vol_confirm)
        if (x > 5 and score > 0) or (x < -5 and score < 0)
    )
    confidence = min(10, max(3, 3 + signals * 2 + int(abs(score) / 20)))

    return {
        "method": "heuristic",
        "score": score,
        "verdict": verdict,
        "confidence": confidence,
        "components": {
            "trend": round(trend, 2),
            "momentum": round(momentum, 2),
            "volume_confirm": round(vol_confirm, 2),
            "range_position": round(position, 2),
        },
        "interpretation": (
            f"近 {built.get('seq_len', 60)} 日价量序列：{summary.get('pattern', '—')}，"
            f"综合得分 {score}（{verdict}）"
        ),
        "_note": "启发式序列分，非 Qlib 官方模型输出；供技术面交叉验证",
    }


def try_torch_tcn_score(
    tensor_conv: list[list[float]],
    *,
    model_path: str | Path | None = None,
) -> dict[str, Any] | None:
    """若安装 torch 且存在权重文件，用 TCN 结构推理。"""
    path = Path(model_path or os.getenv("ALPHA360_MODEL_PATH", DEFAULT_MODEL_PATH))
    if not path.is_file():
        return None
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        return None

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
    state = torch.load(path, map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    model.eval()

    x = torch.tensor([tensor_conv], dtype=torch.float32)
    with torch.no_grad():
        pred = float(model(x).item())

    score = round(_clamp(pred * 100, -100, 100), 2)
    return {
        "method": "tcn",
        "model_path": str(path),
        "score": score,
        "verdict": "序列偏多" if score >= 15 else ("序列偏空" if score <= -15 else "序列中性"),
        "raw_prediction": round(pred, 6),
        "_note": "TCN 权重需自行用 Qlib 训练后放到 models/alpha360_tcn.pt",
    }


def score_alpha360(built: dict[str, Any]) -> dict[str, Any]:
    """优先 TCN 权重推理，否则启发式。"""
    tensor_conv = built.get("tensor_conv")
    if tensor_conv:
        tcn = try_torch_tcn_score(tensor_conv)
        if tcn:
            return tcn
    return score_alpha360_heuristic(built)


def get_alpha360_score(
    client: EastMoneyClient,
    secid: str,
    *,
    seq_len: int = 60,
    period: str = "daily",
    adjust: str = "qfq",
    include_tensor: bool = False,
) -> dict[str, Any]:
    """Alpha360 张量 + 序列打分（默认不返回完整矩阵）。"""
    built = get_alpha360_tensor(
        client,
        secid,
        seq_len=seq_len,
        period=period,
        adjust=adjust,
        include_tensor=True,
    )
    built["inference"] = score_alpha360(built)
    if not include_tensor:
        built.pop("tensor_rnn", None)
        built.pop("tensor_conv", None)
        built.pop("flat_qlib", None)
    return built


def export_alpha360_npy(
    built: dict[str, Any],
    out_dir: str | Path,
    *,
    prefix: str = "alpha360",
) -> dict[str, str]:
    """导出 tensor_conv / tensor_rnn 为 .npy（需 numpy）。"""
    import numpy as np

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    secid = str(built.get("secid", "unknown")).replace(".", "_")
    paths: dict[str, str] = {}

    if built.get("tensor_conv"):
        p = out / f"{prefix}_{secid}_conv.npy"
        np.save(p, np.array(built["tensor_conv"], dtype=np.float32))
        paths["tensor_conv"] = str(p)
    if built.get("tensor_rnn"):
        p = out / f"{prefix}_{secid}_rnn.npy"
        np.save(p, np.array(built["tensor_rnn"], dtype=np.float32))
        paths["tensor_rnn"] = str(p)
    if built.get("flat_qlib"):
        p = out / f"{prefix}_{secid}_flat_qlib.npy"
        np.save(p, np.array(built["flat_qlib"], dtype=np.float32))
        paths["flat_qlib"] = str(p)
    return paths
