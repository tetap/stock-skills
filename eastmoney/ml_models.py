"""量化模型路径与可选 LightGBM / TCN 权重加载。"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
DEFAULT_LGB_PATH = MODEL_DIR / "alpha158_lgb.txt"
DEFAULT_TCN_PATH = MODEL_DIR / "alpha360_tcn.pt"


def _tanh_score(raw: float, *, scale: float = 45) -> float:
    return round(100 * math.tanh(raw / scale), 2)


def alpha158_feature_names(factors: dict[str, float]) -> list[str]:
    """与训练脚本一致的因子名顺序（sorted keys）。"""
    return sorted(factors.keys())


def alpha158_feature_vector(factors: dict[str, float]) -> list[float]:
    return [float(factors.get(k) or 0) for k in alpha158_feature_names(factors)]


def try_lgb158_score(
    factors: dict[str, float],
    *,
    model_path: str | Path | None = None,
) -> dict[str, Any] | None:
    """若存在 LightGBM 权重则推理，否则返回 None 走启发式。"""
    path = Path(model_path or os.getenv("ALPHA158_MODEL_PATH", DEFAULT_LGB_PATH))
    if not path.is_file():
        return None
    try:
        import lightgbm as lgb
    except ImportError:
        return None

    booster = lgb.Booster(model_file=str(path))
    vec = alpha158_feature_vector(factors)
    raw = float(booster.predict([vec])[0])
    score = _tanh_score(raw * 50, scale=35)

    if score >= 20:
        verdict = "因子偏多"
    elif score <= -20:
        verdict = "因子偏空"
    else:
        verdict = "因子中性"

    return {
        "method": "lightgbm",
        "model_path": str(path),
        "score": score,
        "verdict": verdict,
        "raw_prediction": round(raw, 6),
        "interpretation": f"Alpha158 LightGBM 综合 {score}（{verdict}）",
        "_note": "LightGBM 权重来自 models/alpha158_lgb.txt 或 Qlib 训练导出",
    }


def model_status() -> dict[str, Any]:
    """报告当前可用模型（供 get_quant_technical 附加）。"""
    lgb_path = Path(os.getenv("ALPHA158_MODEL_PATH", DEFAULT_LGB_PATH))
    tcn_path = Path(os.getenv("ALPHA360_MODEL_PATH", DEFAULT_TCN_PATH))
    return {
        "alpha158_lightgbm": {
            "path": str(lgb_path),
            "available": lgb_path.is_file(),
        },
        "alpha360_tcn": {
            "path": str(tcn_path),
            "available": tcn_path.is_file(),
        },
        "train_hint": "python scripts/train_quant_models.py --help",
    }
