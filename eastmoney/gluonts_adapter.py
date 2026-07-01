"""GluonTS 公共训练/推理（DeepAR · TFT · PandasDataset 长表）。"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
DEFAULT_DEEPAR_DIR = MODEL_DIR / "gluonts_deepar"
DEFAULT_TFT_DIR = MODEL_DIR / "gluonts_tft"

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

GLUONTS_MODELS: tuple[tuple[str, Path, str], ...] = (
    ("gluonts_tft", DEFAULT_TFT_DIR, "TemporalFusionTransformer"),
    ("gluonts_deepar", DEFAULT_DEEPAR_DIR, "DeepAR"),
)


def _resolve_model_dir(model_kind: str) -> Path:
    env_map = {
        "gluonts_deepar": "GLUONTS_DEEPAR_PATH",
        "gluonts_tft": "GLUONTS_TFT_PATH",
    }
    default_map = {
        "gluonts_deepar": DEFAULT_DEEPAR_DIR,
        "gluonts_tft": DEFAULT_TFT_DIR,
    }
    env = env_map.get(model_kind, "GLUONTS_MODEL_PATH")
    return Path(os.getenv(env, default_map.get(model_kind, DEFAULT_DEEPAR_DIR)))


def gluonts_status() -> dict[str, Any]:
    models: dict[str, Any] = {}
    for kind, default_path, label in GLUONTS_MODELS:
        path = _resolve_model_dir(kind)
        models[kind] = {
            "label": label,
            "model_dir": str(path),
            "model_ready": path.is_dir() and (path / "predictor.json").exists(),
            "metrics": str(path / "metrics.json"),
        }
    return {
        "available": GLUONTS_AVAILABLE,
        "import_error": _IMPORT_ERROR or None,
        "install_hint": "pip install -r requirements-ml.txt",
        "pandas_reference": "https://ts.gluon.ai/stable/tutorials/data_manipulation/pandasdataframes.html",
        "models": models,
    }


def _item_id(secid: str) -> str:
    return secid.replace(".", "_")


def bars_to_long_dataframe(
    secid: str,
    bars: list[dict[str, Any]],
    *,
    target: str = "close",
) -> Any:
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


def _evaluate_gluonts_oos(
    predictor: Any,
    test_df: Any,
    *,
    context_length: int,
    prediction_length: int,
) -> dict[str, float]:
    from eastmoney.backtest import evaluate_predictions

    preds: list[float] = []
    labels: list[float] = []
    for _item_id, grp in test_df.groupby("item_id"):
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

    if len(preds) >= 3:
        return evaluate_predictions(preds, labels)
    return {"ic": 0.0, "direction_accuracy": 0.0, "count": 0, "rmse": 0.0}


def _train_gluonts_model(
    client: Any,
    secids: list[str],
    *,
    model_kind: str,
    out_dir: Path,
    estimator_factory: Callable[..., Any],
    limit: int = 500,
    prediction_length: int = 5,
    context_length: int = 60,
    max_epochs: int = 15,
    train_ratio: float = 0.8,
) -> dict[str, Any]:
    if not GLUONTS_AVAILABLE:
        raise ImportError(_IMPORT_ERROR or "请先 pip install -r requirements-ml.txt")

    from eastmoney.backtest import save_metrics
    from eastmoney.ml_models import evaluate_oos_metrics

    out_dir.mkdir(parents=True, exist_ok=True)
    df = merge_secids_long_df(client, secids, limit=limit)
    train_df, test_df = temporal_train_test_dataframes(df, train_ratio=train_ratio)
    train_ds = build_pandas_dataset(train_df)

    estimator = estimator_factory(
        prediction_length=prediction_length,
        context_length=context_length,
    )
    predictor = estimator.train(train_ds)
    oos_m = _evaluate_gluonts_oos(
        predictor,
        test_df,
        context_length=context_length,
        prediction_length=prediction_length,
    )
    predictor.serialize(out_dir)

    gate = evaluate_oos_metrics(oos_m)
    meta = {
        "model_kind": model_kind,
        "model_dir": str(out_dir),
        "secids": secids,
        "prediction_length": prediction_length,
        "context_length": context_length,
        "train_ratio": train_ratio,
        "series_count": int(df["item_id"].nunique()),
        "best": {"out_of_sample": oos_m},
        "oos_passed": gate["passed"],
        "pandas_format": "long_dataframe(item_id,timestamp,target,feat_dynamic_real)",
        "reference": "https://ts.gluon.ai/stable/tutorials/data_manipulation/pandasdataframes.html",
    }
    save_metrics(str(out_dir / "metrics.json"), meta)
    return meta


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
    from gluonts.torch import Trainer
    from gluonts.torch.model.deepar import DeepAREstimator

    out = out_dir or _resolve_model_dir("gluonts_deepar")

    def factory(*, prediction_length: int, context_length: int) -> DeepAREstimator:
        return DeepAREstimator(
            prediction_length=prediction_length,
            context_length=context_length,
            freq="B",
            trainer=Trainer(max_epochs=max_epochs, batch_size=32, num_batches_per_epoch=50),
        )

    return _train_gluonts_model(
        client,
        secids,
        model_kind="gluonts_deepar",
        out_dir=out,
        estimator_factory=factory,
        limit=limit,
        prediction_length=prediction_length,
        context_length=context_length,
        max_epochs=max_epochs,
        train_ratio=train_ratio,
    )


def train_tft(
    client: Any,
    secids: list[str],
    *,
    out_dir: Path | None = None,
    limit: int = 500,
    prediction_length: int = 5,
    context_length: int = 60,
    max_epochs: int = 10,
    train_ratio: float = 0.8,
) -> dict[str, Any]:
    from gluonts.torch import Trainer
    from gluonts.torch.model.tft import TemporalFusionTransformerEstimator

    out = out_dir or _resolve_model_dir("gluonts_tft")

    def factory(*, prediction_length: int, context_length: int) -> TemporalFusionTransformerEstimator:
        return TemporalFusionTransformerEstimator(
            prediction_length=prediction_length,
            context_length=context_length,
            freq="B",
            trainer=Trainer(max_epochs=max_epochs, batch_size=16, num_batches_per_epoch=50),
        )

    return _train_gluonts_model(
        client,
        secids,
        model_kind="gluonts_tft",
        out_dir=out,
        estimator_factory=factory,
        limit=limit,
        prediction_length=prediction_length,
        context_length=context_length,
        max_epochs=max_epochs,
        train_ratio=train_ratio,
    )


def _forecast_from_dir(
    client: Any,
    secid: str,
    model_dir: Path,
    *,
    model_kind: str,
    method_label: str,
    limit: int = 120,
) -> dict[str, Any] | None:
    if not GLUONTS_AVAILABLE or not (model_dir / "predictor.json").exists():
        return None

    from gluonts.model.predictor import Predictor

    from eastmoney.backtest import get_kline_resilient
    from eastmoney.ml_models import _tanh_score

    bars = get_kline_resilient(client, secid, period="daily", adjust="qfq", limit=limit)
    if len(bars) < 60:
        return None

    df = bars_to_long_dataframe(secid, bars)
    dataset = build_pandas_dataset(df)
    predictor = Predictor.deserialize(model_dir)
    forecasts = list(predictor.predict(dataset))
    if not forecasts:
        return None

    fc = forecasts[0]
    last_close = float(bars[-1]["close"])
    mean_end = float(fc.mean[-1])
    implied_ret = mean_end / last_close - 1 if last_close else 0.0
    score = _tanh_score(implied_ret * 50, scale=35)

    if score >= 20:
        verdict = f"{method_label}偏多"
    elif score <= -20:
        verdict = f"{method_label}偏空"
    else:
        verdict = f"{method_label}中性"

    oos = load_gluonts_oos_status(model_dir=model_dir)
    return {
        "method": model_kind,
        "model_path": str(model_dir),
        "score": score,
        "verdict": verdict,
        "implied_return": round(implied_ret, 6),
        "forecast_horizon": len(fc.mean),
        "oos_passed": oos.get("oos_passed"),
        "interpretation": f"GluonTS {method_label} 隐含 {implied_ret:.2%} → {score}（{verdict}）",
        "_note": f"metrics: {model_dir}/metrics.json",
    }


def try_gluonts_forecast_score(
    client: Any,
    secid: str,
    *,
    limit: int = 120,
) -> dict[str, Any] | None:
    """优先 OOS 通过的 TFT，其次 DeepAR，否则返回首个可用模型。"""
    if not GLUONTS_AVAILABLE:
        return None

    candidates: list[dict[str, Any]] = []
    for kind, default_path, label in GLUONTS_MODELS:
        path = _resolve_model_dir(kind)
        row = _forecast_from_dir(client, secid, path, model_kind=kind, method_label=label, limit=limit)
        if row:
            candidates.append(row)

    if not candidates:
        return None

    passed = [c for c in candidates if c.get("oos_passed") is True]
    return passed[0] if passed else candidates[0]


def load_gluonts_oos_status(*, model_dir: str | Path | None = None, model_kind: str = "gluonts_deepar") -> dict[str, Any]:
    path = Path(model_dir) if model_dir else _resolve_model_dir(model_kind)
    metrics_path = path / "metrics.json"
    base = {"metrics_path": str(metrics_path), "model_dir": str(path), "model_kind": model_kind}
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
            "model_kind": data.get("model_kind", model_kind),
        }
    except (OSError, ValueError, TypeError):
        return {**base, "available": False, "oos_passed": None, "reason": "metrics_read_error"}


# 兼容旧 import
DEFAULT_GLUONTS_DIR = DEFAULT_DEEPAR_DIR
