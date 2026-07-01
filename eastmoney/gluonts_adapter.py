"""GluonTS PandasDataset 适配：K 线 → 长表 → DeepAR 训练/推理。

参考: https://ts.gluon.ai/stable/tutorials/data_manipulation/pandasdataframes.html
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
DEFAULT_GLUONTS_DIR = MODEL_DIR / "gluonts_deepar"

GLUONTS_AVAILABLE = False
_IMPORT_ERROR = ""

try:
    import pandas as pd
    from gluonts.dataset.pandas import PandasDataset

    GLUONTS_AVAILABLE = True
except ImportError as exc:  # pragma: no cover
    pd = None  # type: ignore
    PandasDataset = None  # type: ignore
    _IMPORT_ERROR = str(exc)


def gluonts_status() -> dict[str, Any]:
    path = Path(os.getenv("GLUONTS_MODEL_PATH", DEFAULT_GLUONTS_DIR))
    return {
        "available": GLUONTS_AVAILABLE,
        "model_dir": str(path),
        "model_ready": path.is_dir() and (path / "predictor.json").exists(),
        "import_error": _IMPORT_ERROR or None,
        "install_hint": "pip install -r requirements-ml.txt  # 含 gluonts[torch]",
    }


def _item_id(secid: str) -> str:
    return secid.replace(".", "_")


def bars_to_long_dataframe(
    secid: str,
    bars: list[dict[str, Any]],
    *,
    target: str = "close",
) -> Any:
    """单股 K 线 → GluonTS 长表（item_id + timestamp + target + 动态特征）。"""
    if not GLUONTS_AVAILABLE or pd is None:
        raise ImportError(_IMPORT_ERROR or "gluonts 未安装")

    rows: list[dict[str, Any]] = []
    item = _item_id(secid)
    prev_close: float | None = None
    for bar in bars:
        close = float(bar["close"])
        ret = 0.0 if prev_close is None else close / prev_close - 1
        rows.append(
            {
                "item_id": item,
                "timestamp": pd.Timestamp(str(bar["date"])),
                "target": close if target == "close" else ret,
                "volume": float(bar.get("volume") or 0),
                "return_1d": ret,
            }
        )
        prev_close = close
    return pd.DataFrame(rows)


def merge_secids_long_df(client: Any, secids: list[str], *, limit: int = 500) -> Any:
    from eastmoney.backtest import get_kline_resilient

    frames = []
    for secid in secids:
        bars = get_kline_resilient(client, secid, period="daily", adjust="qfq", limit=limit)
        if len(bars) < 80:
            continue
        frames.append(bars_to_long_dataframe(secid, bars))
    if not frames:
        raise ValueError("无足够 K 线构建 PandasDataset")
    return pd.concat(frames, ignore_index=True)


def build_pandas_dataset(df: Any, *, freq: str = "B") -> Any:
    """长表 → GluonTS PandasDataset（含动态实特征 volume/return_1d）。"""
    if PandasDataset is None:
        raise ImportError(_IMPORT_ERROR or "gluonts 未安装")
    return PandasDataset.from_long_dataframe(
        df,
        target="target",
        timestamp="timestamp",
        item_id="item_id",
        feat_dynamic_real=["volume", "return_1d"],
        freq=freq,
    )


def temporal_train_test_dataframes(
    df: Any,
    *,
    train_ratio: float = 0.8,
) -> tuple[Any, Any]:
    """长表按全局时间切分 train/test。"""
    if pd is None:
        raise ImportError(_IMPORT_ERROR or "gluonts 未安装")
    cutoff = df["timestamp"].quantile(train_ratio)
    train_df = df[df["timestamp"] <= cutoff].copy()
    test_df = df[df["timestamp"] > cutoff].copy()
    if train_df.empty:
        train_df = df.copy()
    if test_df.empty:
        test_df = df.tail(max(10, len(df) // 5)).copy()
    return train_df, test_df


def train_deepar(
    client: Any,
    secids: list[str],
    *,
    out_dir: Path | None = None,
    limit: int = 500,
    prediction_length: int = 5,
    context_length: int = 60,
    max_epochs: int = 15,
    train_ratio: float = 0.8,
) -> dict[str, Any]:
    if not GLUONTS_AVAILABLE:
        raise ImportError(_IMPORT_ERROR or "请先 pip install -r requirements-ml.txt")

    from gluonts.torch import Trainer
    from gluonts.torch.model.deepar import DeepAREstimator

    from eastmoney.backtest import evaluate_predictions, save_metrics
    from eastmoney.ml_models import evaluate_oos_metrics

    out = out_dir or DEFAULT_GLUONTS_DIR
    out.mkdir(parents=True, exist_ok=True)

    df = merge_secids_long_df(client, secids, limit=limit)
    train_df, test_df = temporal_train_test_dataframes(df, train_ratio=train_ratio)
    train_ds = build_pandas_dataset(train_df)

    estimator = DeepAREstimator(
        prediction_length=prediction_length,
        context_length=context_length,
        freq="B",
        trainer=Trainer(max_epochs=max_epochs, batch_size=32, num_batches_per_epoch=50),
    )
    predictor = estimator.train(train_ds)

    # OOS：测试集各序列末段 implied return vs 实际 5 日收益
    preds: list[float] = []
    labels: list[float] = []
    for item_id, grp in test_df.groupby("item_id"):
        grp = grp.sort_values("timestamp")
        if len(grp) < context_length + prediction_length + 1:
            continue
        sub = grp.iloc[-(context_length + prediction_length) :].copy()
        ds = build_pandas_dataset(sub.iloc[:context_length])
        fc = list(predictor.predict(ds))[0]
        last_close = float(sub.iloc[context_length - 1]["target"])
        pred_close = float(fc.mean[-1])
        actual_close = float(sub.iloc[min(context_length + prediction_length - 1, len(sub) - 1)]["target"])
        if last_close <= 0:
            continue
        preds.append(pred_close / last_close - 1)
        labels.append(actual_close / last_close - 1)

    oos_m = evaluate_predictions(preds, labels) if len(preds) >= 3 else {
        "ic": 0.0,
        "direction_accuracy": 0.0,
        "count": 0,
        "rmse": 0.0,
    }

    predictor.serialize(out)
    meta = {
        "model_kind": "gluonts_deepar",
        "model_dir": str(out),
        "secids": secids,
        "prediction_length": prediction_length,
        "context_length": context_length,
        "train_ratio": train_ratio,
        "series_count": int(df["item_id"].nunique()),
        "best": {"out_of_sample": oos_m},
        "pandas_format": "long_dataframe(item_id,timestamp,target,feat_dynamic_real)",
        "reference": "https://ts.gluon.ai/stable/tutorials/data_manipulation/pandasdataframes.html",
    }
    gate = evaluate_oos_metrics(oos_m)
    meta["oos_passed"] = gate["passed"]
    save_metrics(str(out / "metrics.json"), meta)
    return meta


def try_gluonts_forecast_score(
    client: Any,
    secid: str,
    *,
    model_dir: str | Path | None = None,
    limit: int = 120,
) -> dict[str, Any] | None:
    """DeepAR 预测未来路径 → 量化分数。"""
    if not GLUONTS_AVAILABLE:
        return None
    path = Path(model_dir or os.getenv("GLUONTS_MODEL_PATH", DEFAULT_GLUONTS_DIR))
    if not (path / "predictor.json").exists():
        return None

    from gluonts.model.predictor import Predictor

    from eastmoney.backtest import get_kline_resilient
    from eastmoney.ml_models import _tanh_score

    bars = get_kline_resilient(client, secid, period="daily", adjust="qfq", limit=limit)
    if len(bars) < 60:
        return None

    df = bars_to_long_dataframe(secid, bars)
    dataset = build_pandas_dataset(df)
    predictor = Predictor.deserialize(path)
    forecasts = list(predictor.predict(dataset))
    if not forecasts:
        return None

    fc = forecasts[0]
    last_close = float(bars[-1]["close"])
    mean_end = float(fc.mean[-1])
    implied_ret = mean_end / last_close - 1 if last_close else 0.0
    score = _tanh_score(implied_ret * 50, scale=35)

    if score >= 20:
        verdict = "DeepAR偏多"
    elif score <= -20:
        verdict = "DeepAR偏空"
    else:
        verdict = "DeepAR中性"

    return {
        "method": "gluonts_deepar",
        "model_path": str(path),
        "score": score,
        "verdict": verdict,
        "implied_return": round(implied_ret, 6),
        "forecast_horizon": len(fc.mean),
        "interpretation": f"GluonTS DeepAR 隐含 {implied_ret:.2%} → {score}（{verdict}）",
        "_note": "PandasDataset 长表训练；详见 models/gluonts_deepar/metrics.json",
    }


def load_gluonts_oos_status(*, model_dir: str | Path | None = None) -> dict[str, Any]:
    path = Path(model_dir or os.getenv("GLUONTS_MODEL_PATH", DEFAULT_GLUONTS_DIR))
    metrics_path = path / "metrics.json"
    base = {"metrics_path": str(metrics_path), "model_dir": str(path)}
    if not metrics_path.is_file():
        return {**base, "available": False, "oos_passed": None, "reason": "no_metrics"}
    try:
        from eastmoney.ml_models import evaluate_oos_metrics

        data = json.loads(metrics_path.read_text(encoding="utf-8"))
        oos = (data.get("best") or {}).get("out_of_sample") or {}
        gate = evaluate_oos_metrics(oos)
        return {
            **base,
            "available": True,
            "oos_passed": gate["passed"],
            "out_of_sample": oos,
            "model_kind": data.get("model_kind"),
        }
    except (OSError, ValueError, TypeError):
        return {**base, "available": False, "oos_passed": None, "reason": "metrics_read_error"}
