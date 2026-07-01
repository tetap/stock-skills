---
name: stock-sector
description: >-
  A 股板块分析/选股。手动调用 /stock-sector 或 $stock-sector。板块走势+推荐几只走 sector-report。
disable-model-invocation: true
argument-hint: "[板块名称，或 今日/热点/推荐几只]"
---

# 板块分析

用户在本条消息 **`/stock-sector` 或 `$stock-sector` 后面**的文字可能是板块名（如 `半导体`），或留空 / `今日` / `热点` / **「推荐几只」**。

## 路由

| 意图 | 模板 |
|------|------|
| 只看板块涨跌/成分 | stock-sector-analysis |
| **走势 + 推荐/看好/龙头** | **stock-main → sector-report.md** |

## 必做（选股场景）

1. 工具 **≥12 次** + 候选股轻扫
2. `get_market_news`（flash + keyword + xueqiu_hot）
3. `get_review_protocol(flow=C)` → §6 审核纪要
4. 末尾免责声明
