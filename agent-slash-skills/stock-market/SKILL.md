---
name: stock-market
description: >-
  A 股市场热点与情绪简报。/stock-market 或 $stock-market。无单一标的，走 market-brief D 流程。
disable-model-invocation: true
argument-hint: "[今天热点 / 情绪 / 留空]"
---

# 市场热点 / 情绪

用户在本条 **`/stock-market` 或 `$stock-market` 后面**可描述热点/情绪，或留空。

同 **`/stock 今天有什么热点`** → **market-brief.md**。

## 必做

1. 工具见 market-brief.md（快讯 + 板块 + 资金）
2. `get_review_protocol(flow=D)` → 审核纪要
3. §1 给可验证判断，禁止空泛「有热点」
4. 末尾免责声明

## 边界

- **不是**个股全量分析 → 若出现具体股票「能不能买」，改 `/stock 分析 {标的}`
