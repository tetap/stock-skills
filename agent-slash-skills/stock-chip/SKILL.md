---
name: stock-chip
description: >-
  A 股筹码单维度分析。/stock-chip 或 $stock-chip。非全量报告。
disable-model-invocation: true
argument-hint: "[股票名称或代码]"
---

# 筹码分析（单维度）

用户在本条 **`/stock-chip` 或 `$stock-chip` 后面**的文字是股票名称或代码。

## 你要做的

1. 读取 **stock-chip-analysis** skill
2. `get_chip_distribution`、现价、可选 K 线
3. 成本区、集中度、现价相对位置
4. 末尾免责声明

## 边界

- **仅筹码维度**，不走 review-protocol
- 要买/全量 → **`/stock 分析 {标的}`**
