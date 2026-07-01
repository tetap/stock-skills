"""Alpha360 序列打分：启发式特征 + 可选 PyTorch TCN 推理。"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any

from eastmoney.alpha360 import build_alpha360_from_bars, get_alpha360_tensor
from eastmoney.client import EastMoneyClient

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "alpha360_tcn.pt"


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _tanh_score(raw: float, *, scale: float = 45, cap: float | None = None) -> float:
    """压缩极端 raw；cap 用于限制 5 日窗口顶格（默认不 cap）。"""
    score = round(100 * math.tanh(raw / scale), 2)
    if cap is not None:
        score = max(-cap, min(cap, score))
    return score


def _verdict_from_score(score: float) -> str:
    if score >= 20:
        return "序列偏多"
    if score <= -20:
        return "序列偏空"
    return "序列中性"


def _score_segment(
    close_series: list[float],
    volume_series: list[float],
    *,
    low_pct: float,
    high_pct: float,
    change_pct: float | None,
    slope: float,
    vol_ratio: float | None,
    short_window: bool = False,
) -> dict[str, Any]:
    """单窗口序列打分（归一化 close 序列）。"""
    chg = float(change_pct or 0)
    vr = float(vol_ratio or 1)

    trend = slope * 2500
    momentum = chg * 1.2
    vol_confirm = (vr - 1) * 12
    if trend * vol_confirm < 0:
        vol_confirm *= 0.35

    range_pct = high_pct - low_pct
    position = 0.0
    if range_pct > 0.1 and close_series:
        pos_in_range = (close_series[-1] - (1 + low_pct / 100)) / (range_pct / 100 + 1e-9)
        position = (pos_in_range - 0.5) * 12

    raw = trend + momentum + vol_confirm + position
    if short_window:
        score = _tanh_score(raw, scale=52, cap=85)
    else:
        score = _tanh_score(raw, scale=45)
    return {
        "score": score,
        "verdict": _verdict_from_score(score),
        "raw": round(raw, 3),
        "components": {
            "trend": round(trend, 2),
            "momentum": round(momentum, 2),
            "volume_confirm": round(vol_confirm, 2),
            "range_position": round(position, 2),
        },
    }


def score_alpha360_heuristic(built: dict[str, Any]) -> dict[str, Any]:
    """基于 6×60 张量：分别计算 5 日/60 日序列分，再合成。"""
    summary = built.get("sequence_summary") or {}
    tensor_rnn = built.get("tensor_rnn") or []
    close_series = [row[3] for row in tensor_rnn] if tensor_rnn else []
    volume_series = [row[5] for row in tensor_rnn] if tensor_rnn else []

    high_pct = float(summary.get("high_vs_ref_close_pct") or 0)
    low_pct = float(summary.get("low_vs_ref_close_pct") or 0)
    vol_ratio = summary.get("volume_ratio_late_early")

    seg_5 = _score_segment(
        close_series[-5:],
        volume_series[-5:],
        low_pct=low_pct,
        high_pct=high_pct,
        change_pct=summary.get("close_change_5d_pct"),
        slope=float(summary.get("close_slope_5d") or 0),
        vol_ratio=vol_ratio,
        short_window=True,
    )
    seg_60 = _score_segment(
        close_series,
        volume_series,
        low_pct=low_pct,
        high_pct=high_pct,
        change_pct=summary.get("close_change_20d_pct"),
        slope=float(summary.get("close_slope_norm") or 0),
        vol_ratio=vol_ratio,
    )

    # 合成：短周期权重更高，便于捕捉反弹
    combined = round(seg_60["score"] * 0.4 + seg_5["score"] * 0.6, 2)
    divergence = seg_5["verdict"] != seg_60["verdict"]

    signals = sum(
        1
        for seg in (seg_5, seg_60)
        if abs(seg["score"]) >= 20
    )
    confidence = min(10, max(3, 3 + signals * 2 + int(abs(combined) / 25)))

    interp = (
        f"5日 {seg_5['score']}（{seg_5['verdict']}，{summary.get('pattern_5d', '—')}）· "
        f"60日 {seg_60['score']}（{seg_60['verdict']}，{summary.get('pattern_60d', '—')}）· "
        f"合成 {combined}"
    )
    if divergence:
        interp += " · 短/长序列分歧，报告须分开解读"

    return {
        "method": "heuristic",
        "score": combined,
        "score_5d": seg_5["score"],
        "score_60d": seg_60["score"],
        "verdict": _verdict_from_score(combined),
        "verdict_5d": seg_5["verdict"],
        "verdict_60d": seg_60["verdict"],
        "divergence": divergence,
        "confidence": confidence,
        "components": {
            "short_5d": seg_5["components"],
            "medium_60d": seg_60["components"],
        },
        "interpretation": interp,
        "_note": "启发式序列分；score=0.4×60日+0.6×5日，非 Qlib 官方模型",
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
    except ImportError:
        return None

    from eastmoney.tcn_model import TCNScore

    model = TCNScore()
    state = torch.load(path, map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    model.eval()

    x = torch.tensor([tensor_conv], dtype=torch.float32)
    with torch.no_grad():
        pred = float(model(x).item())

    score = _tanh_score(pred * 50, scale=50)
    return {
        "method": "tcn",
        "model_path": str(path),
        "score": score,
        "score_60d": score,
        "verdict": _verdict_from_score(score),
        "raw_prediction": round(pred, 6),
        "_note": "TCN 权重需自行用 Qlib 训练后放到 models/alpha360_tcn.pt",
    }


def score_alpha360(built: dict[str, Any]) -> dict[str, Any]:
    """优先 TCN 权重（60 日）+ 启发式 5/60 分解，否则纯启发式。"""
    heuristic = score_alpha360_heuristic(built)
    tensor_conv = built.get("tensor_conv")
    if not tensor_conv:
        return heuristic

    tcn = try_torch_tcn_score(tensor_conv)
    if not tcn:
        return heuristic

    s5 = float(heuristic.get("score_5d") or 0)
    s60 = float(tcn.get("score") or heuristic.get("score_60d") or 0)
    combined = round(s60 * 0.4 + s5 * 0.6, 2)
    return {
        **heuristic,
        "method": "tcn+heuristic",
        "model_path": tcn.get("model_path"),
        "score": combined,
        "score_60d": s60,
        "score_5d": s5,
        "verdict": _verdict_from_score(combined),
        "verdict_60d": _verdict_from_score(s60),
        "tcn_raw_prediction": tcn.get("raw_prediction"),
        "_note": "60 日来自 TCN 权重，5 日仍为启发式；合成=0.4×60+0.6×5",
    }


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
