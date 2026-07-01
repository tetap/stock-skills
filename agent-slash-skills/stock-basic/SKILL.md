---
name: stock-basic
description: >-
  A 股基本面单维度分析。/stock-basic 或 $stock-basic。非全量报告。
disable-model-invocation: true
argument-hint: "[股票名称或代码]"
---

# 基本面分析（单维度）

用户在本条 **`/stock-basic` 或 `$stock-basic` 后面**的文字是股票名称或代码。

## 你要做的

1. 读取 **stock-fundamental-analysis** skill
2. 公司简介、财报、估值
3. 概况、财务趋势、风险点
4. 末尾免责声明

## 边界

- **仅基本面**，不走 review-protocol
- 要买/全量 → **`/stock 分析 {标的}`**
