---
name: stock-fund
description: >-
  A 股资金面分析。手动调用 /stock-fund 或 $stock-fund，分析主力净流入与背离。
disable-model-invocation: true
argument-hint: "[股票名称或代码]"
---

# 资金面分析

用户在本条消息 **`/stock-fund` 或 `$stock-fund` 后面**的文字是股票名称或代码。

## 你要做的

1. 读取并遵循 **stock-capital-flow** skill
2. 拉取 `get_stock_fund_flow`、必要时排名与大盘背景
3. 说明主力趋势、价量背离、板块背景
4. 末尾加免责声明
