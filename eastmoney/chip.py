"""筹码分布。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import CHIP_URL


def get_chip_distribution(
    client: EastMoneyClient,
    secid: str,
    *,
    limit: int = 60,
) -> list[dict[str, Any]]:
    params = {
        "secid": secid,
        "lmt": str(limit),
    }
    data = client.get_json(
        CHIP_URL,
        params,
        cache_key=f"chip:{secid}:{limit}",
        cache_ttl=14400,
    )
    klines = (data.get("data") or {}).get("klines") or []
    rows: list[dict[str, Any]] = []
    for line in klines:
        parts = line.split(",")
        if len(parts) < 9:
            continue
        rows.append(
            {
                "date": parts[0],
                "profit_ratio": float(parts[1]) if parts[1] else None,
                "avg_cost": float(parts[2]) if parts[2] else None,
                "cost_90_low": float(parts[3]) if parts[3] else None,
                "cost_90_high": float(parts[4]) if parts[4] else None,
                "concentration_90": float(parts[5]) if parts[5] else None,
                "cost_70_low": float(parts[6]) if parts[6] else None,
                "cost_70_high": float(parts[7]) if parts[7] else None,
                "concentration_70": float(parts[8]) if parts[8] else None,
            }
        )
    return rows
