#!/usr/bin/env python3
"""导出 Alpha360 张量为 .npy，供 PyTorch / Qlib 训练脚本使用。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eastmoney.alpha360_infer import export_alpha360_npy, get_alpha360_score  # noqa: E402
from eastmoney.tools import run_tool  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="导出 Alpha360 张量")
    parser.add_argument("--secid", required=True)
    parser.add_argument("--out-dir", default="output/alpha360")
    parser.add_argument("--seq-len", type=int, default=60)
    parser.add_argument("--with-score", action="store_true", help="同时打印序列打分 JSON")
    args = parser.parse_args()

    built = run_tool(
        "get_alpha360_score",
        secid=args.secid,
        seq_len=args.seq_len,
        include_tensor=True,
    )
    paths = export_alpha360_npy(built, args.out_dir)
    print(json.dumps({"exported": paths, "layouts": built.get("layouts")}, ensure_ascii=False, indent=2))
    if args.with_score:
        print(json.dumps(built.get("inference"), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
