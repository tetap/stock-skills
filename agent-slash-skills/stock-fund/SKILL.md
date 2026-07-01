---
name: stock-fund
description: >-
  A 股资金面单维度分析。/stock-fund 或 $stock-fund。非全量报告；要买能介入请用 /stock 分析。
disable-model-invocation: true
argument-hint: "[股票名称或代码]"
---

# 资金面分析（单维度）

用户在本条 **`/stock-fund` 或 `$stock-fund` 后面**的文字是股票名称或代码。

## 你要做的

1. 读取 **stock-capital-flow** skill
2. `get_stock_fund_flow`、必要时 `get_fund_flow_rank` / `get_market_fund_flow`
3. 说明主力趋势、价量背离、板块背景
4. 末尾免责声明

## 边界

- **仅资金面**，不拉基本面三表/筹码/全量新闻，**不走** review-protocol / §7
- 若用户问 **能不能买 / 全量分析 / 介入区间** → **`/stock 分析 {标的}`**
