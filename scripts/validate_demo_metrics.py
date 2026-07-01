#!/usr/bin/env python3
"""校验演示 LGB 权重与 OOS metrics（路径可移植 + 门槛说明）。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eastmoney.ml_models import evaluate_oos_metrics, load_lgb_oos_status


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 models/alpha158_lgb.*")
    parser.add_argument(
        "--metrics",
        type=Path,
        default=ROOT / "models" / "alpha158_lgb.metrics.json",
    )
    parser.add_argument(
        "--strict-oos",
        action="store_true",
        help="OOS 未通过时返回非零退出码（演示权重默认未过，通常不加此参数）",
    )
    args = parser.parse_args()

    metrics_path = args.metrics
    if not metrics_path.is_file():
        print(f"[validate] 缺少 metrics: {metrics_path}", file=sys.stderr)
        return 1

    data = json.loads(metrics_path.read_text(encoding="utf-8"))
    model_ref = str(data.get("model") or "")
    if model_ref.startswith("/"):
        print(f"[validate] model 路径应为仓库相对路径，当前: {model_ref}", file=sys.stderr)
        return 1

    model_path = ROOT / model_ref if model_ref else metrics_path.with_suffix(".txt")
    if not model_path.is_file():
        print(f"[validate] 权重文件不存在: {model_path}", file=sys.stderr)
        return 1

    oos = (data.get("best") or {}).get("out_of_sample") or {}
    gate = evaluate_oos_metrics(oos)
    status = load_lgb_oos_status(model_path=model_path)

    print(f"[validate] model={model_ref}")
    print(f"[validate] OOS IC={gate['ic']:.4f}  dir_acc={gate['direction_accuracy']:.2%}")
    print(f"[validate] {gate['summary']}")
    print(f"[validate] report_cap={status.get('report_cap') or '无（已通过）'}")

    if args.strict_oos and not gate["passed"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
