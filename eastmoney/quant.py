"""量化技术面综合：Alpha158 + Alpha360 + quant_verdict。"""

from __future__ import annotations

from typing import Any

from eastmoney.alpha158 import get_alpha158_score
from eastmoney.alpha360_infer import get_alpha360_score
from eastmoney.client import EastMoneyClient
from eastmoney.ml_models import load_lgb_oos_status, model_status


def _band(score: float) -> str:
    if score >= 20:
        return "偏多"
    if score <= -20:
        return "偏空"
    return "中性"


def build_quant_verdict(
    alpha158: dict[str, Any],
    alpha360: dict[str, Any],
) -> dict[str, Any]:
    """合并表格因子与序列（含 5 日/60 日）打分，生成报告用 verdict。"""
    a158 = alpha158.get("inference") or {}
    a360 = alpha360.get("inference") or {}

    s158 = float(a158.get("score") or 0)
    s360 = float(a360.get("score") or 0)
    s5 = float(a360.get("score_5d") if a360.get("score_5d") is not None else s360)
    s60 = float(a360.get("score_60d") if a360.get("score_60d") is not None else s360)

    b158 = _band(s158)
    b5 = _band(s5)
    b60 = _band(s60)
    divergence = (b5 != b60) or (abs(s158) >= 20 and b158 != b60)

    summary = "量化中性"
    detail = "158 与 360 均未给出强方向，需结合基本面/资金/事件定夺。"

    # --- 短长序列分歧（优先于同向分支）---
    if b5 == "偏多" and b60 == "偏空":
        if b158 == "中性":
            summary = "反弹脉冲·因子未跟上"
            detail = (
                "近 5 日序列转强，但 60 日仍弱且 Alpha158 因子未同步转多；"
                "宜超短博弈，警惕一日游。"
            )
        elif b158 == "偏空":
            summary = "反弹脉冲·因子未跟上"
            detail = (
                "短序列反弹但 Alpha158 仍偏空、60 日趋势未修复；"
                "脉冲性质强，不宜按中线转多理解。"
            )
        else:
            summary = "短线改善·中线仍弱"
            detail = (
                "近 5 日序列转强且 158 略偏多，但 60 日形态仍偏空；"
                "宜按超短/事件博弈，中线需等 60 日趋势修复。"
            )

    elif b5 == "偏空" and b60 == "偏多":
        summary = "短线回调·中线尚稳"
        detail = "60 日序列仍偏多，但近 5 日走弱；适合等回调至支撑再评估。"

    # --- 5/60 同向 ---
    elif b5 == b60 == "偏空":
        summary = "量化偏空"
        if b158 == "中性":
            detail = (
                "5/60 日序列同向偏空，Alpha158 因子尚未极端确认；"
                "技术面压制为主。"
            )
        elif b158 == "偏空":
            detail = "表格与 5/60 日序列同向偏空，技术面压制明显。"
        else:
            summary = "序列偏空·因子未同步"
            detail = (
                "5/60 日序列同向偏空，但 Alpha158 仍偏多；"
                "疑为假突破或因子滞后，宜观望。"
            )

    elif b5 == b60 == "偏多":
        if b158 == "中性":
            summary = "序列偏多·因子未确认"
            detail = (
                "5/60 日序列同向偏多，Alpha158 因子尚未确认；"
                "宜等因子同步或放量突破后再加重仓位。"
            )
        elif b158 == "偏多":
            summary = "量化偏多"
            detail = "表格与 5/60 日序列同向偏多，趋势与因子共振。"
        else:
            summary = "序列转强·因子滞后"
            detail = (
                "短中期序列已偏多，但 Alpha158 因子仍偏空；"
                "反弹能否延续取决于因子是否跟进。"
            )

    # --- 158 与 60 日分歧（5 日已单独处理过的不再进入）---
    elif b158 == "偏多" and b60 == "偏空":
        summary = "因子改善·序列未确认"
        detail = "表格因子略强，时序 60 日未确认反转；需放量收复关键均线后再看。"

    elif b158 == "偏空" and b5 == "偏多" and b60 != "偏空":
        summary = "反弹脉冲·因子未跟上"
        detail = "短序列反弹但 Alpha158 因子尚未同步转强，警惕一日游。"

    elif b158 == "偏空" and b60 == "偏空" and b5 == "中性":
        summary = "量化偏空"
        detail = "60 日与 158 同向偏空，近 5 日尚未修复；仍以趋势压制为主。"

    elif b158 == "偏多" and b60 == "偏多" and b5 == "中性":
        summary = "量化偏多"
        detail = "158 与 60 日同向偏多，近 5 日暂中性；趋势尚可，等待短周期确认。"

    return {
        "summary": summary,
        "detail": detail,
        "divergence": divergence,
        "scores": {
            "alpha158": s158,
            "alpha360_combined": s360,
            "alpha360_5d": s5,
            "alpha360_60d": s60,
        },
        "bands": {
            "alpha158": b158,
            "alpha360_5d": b5,
            "alpha360_60d": b60,
        },
        "_note": "启发式量化结论，须与 MA/资金/新闻交叉验证",
    }


def get_quant_technical(
    client: EastMoneyClient,
    secid: str,
    *,
    period: str = "daily",
    adjust: str = "qfq",
) -> dict[str, Any]:
    """一次拉齐 Alpha158 + Alpha360（含 5/60 日序列分）+ quant_verdict。"""
    a158 = get_alpha158_score(client, secid, period=period, adjust=adjust)
    a360 = get_alpha360_score(client, secid, period=period, adjust=adjust)
    oos = load_lgb_oos_status()
    verdict = build_quant_verdict(a158, a360)
    if oos.get("report_cap"):
        verdict = dict(verdict)
        verdict["oos_warning"] = oos["report_cap"]

    gluonts_score = None
    try:
        from eastmoney.gluonts_adapter import try_gluonts_forecast_score

        gluonts_score = try_gluonts_forecast_score(client, secid)
    except Exception:
        gluonts_score = None

    if gluonts_score and gluonts_score.get("score") is not None:
        verdict = dict(verdict)
        verdict["gluonts_deepar"] = {
            "score": gluonts_score["score"],
            "verdict": gluonts_score.get("verdict"),
            "implied_return": gluonts_score.get("implied_return"),
        }

    return {
        "secid": secid,
        "latest_date": a158.get("latest_date") or a360.get("end_date"),
        "model_status": model_status(),
        "oos_status": oos,
        "timeseries_forecast": gluonts_score,
        "alpha158": {
            "factor_count": a158.get("factor_count"),
            "factor_count_note": a158.get("factor_count_note"),
            "highlights": a158.get("highlights"),
            "inference": a158.get("inference"),
        },
        "alpha360": {
            "sequence_summary": a360.get("sequence_summary"),
            "inference": a360.get("inference"),
        },
        "quant_verdict": verdict,
    }
