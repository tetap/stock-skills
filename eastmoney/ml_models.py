"""量化模型路径与可选 LightGBM / TCN 权重加载。"""

from __future__ import annotations

import json
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


def evaluate_oos_metrics(oos: dict[str, Any]) -> dict[str, Any]:
    """样本外最低门槛：IC > 0 且 direction_accuracy > 50%（与 stock-quant-research 一致）。"""
    ic = float(oos.get("ic") or 0)
    dir_acc = float(oos.get("direction_accuracy") or 0)
    passed = ic > 0 and dir_acc > 0.5
    return {
        "passed": passed,
        "ic": ic,
        "direction_accuracy": dir_acc,
        "threshold": {
            "ic_min_exclusive": 0.0,
            "direction_accuracy_min_exclusive": 0.5,
        },
        "summary": (
            "OOS 通过"
            if passed
            else f"OOS 未通过（IC={ic:.4f}≤0 或 dir_acc={dir_acc:.2%}≤50%）"
        ),
    }


def load_lgb_oos_status(*, model_path: str | Path | None = None) -> dict[str, Any]:
    """读取 LightGBM 训练产出的 OOS 指标（alpha158_lgb.metrics.json）。"""
    path = Path(model_path or os.getenv("ALPHA158_MODEL_PATH", DEFAULT_LGB_PATH))
    metrics_path = path.with_suffix(".metrics.json")
    base = {
        "metrics_path": str(metrics_path),
        "model_path": str(path),
    }
    if not path.is_file():
        return {
            **base,
            "available": False,
            "oos_passed": None,
            "reason": "no_model",
            "report_cap": "无 LGB 权重，quant 为启发式；评级须与 MA/资金/新闻交叉验证",
        }
    if not metrics_path.is_file():
        return {
            **base,
            "available": False,
            "oos_passed": None,
            "reason": "no_metrics_file",
            "report_cap": "LGB 权重存在但未找到 OOS 指标；quant 仅辅助，评级上限「右侧等待」",
        }
    try:
        data = json.loads(metrics_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {
            **base,
            "available": False,
            "oos_passed": None,
            "reason": "metrics_read_error",
            "report_cap": "OOS 指标读取失败；quant 仅辅助",
        }

    oos = (data.get("best") or {}).get("out_of_sample") or {}
    gate = evaluate_oos_metrics(oos)
    passed = gate["passed"]
    return {
        **base,
        "available": True,
        "oos_passed": passed,
        "out_of_sample": oos,
        "train_ratio": data.get("train_ratio"),
        "sample_count": data.get("sample_count"),
        "report_cap": (
            None
            if passed
            else "LGB 未过 OOS（IC≤0 或方向准确率≤50%）；quant 仅辅助，评级上限「右侧等待」"
        ),
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
        "oos_status": load_lgb_oos_status(model_path=lgb_path),
        "train_hint": "python scripts/train_quant_models.py --help",
    }
