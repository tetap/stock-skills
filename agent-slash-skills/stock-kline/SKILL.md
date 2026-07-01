---
name: stock-kline
description: >-
  A 股技术面/K线单维度分析。/stock-kline 或 $stock-kline。非全量报告。
disable-model-invocation: true
argument-hint: "[股票名称或代码]"
---

# 技术面 / K 线（单维度）

用户在本条 **`/stock-kline` 或 `$stock-kline` 后面**的文字是股票名称或代码。

## 你要做的

1. 读取 **stock-technical-analysis** skill
2. 日 K、实时价、MA；可选 `get_quant_technical`（注明 quant 非策略信号）
3. 趋势、支撑/压力、量价
4. 末尾免责声明

## 边界

- **仅技术面**，不走 review-protocol
- 要买/全量 → **`/stock 分析 {标的}`**
