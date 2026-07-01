---
name: stock-kline
description: >-
  A 股技术面/K线分析。手动调用 /stock-kline 或 $stock-kline。
disable-model-invocation: true
argument-hint: "[股票名称或代码]"
---

# 技术面 / K 线

用户在本条消息 **`/stock-kline` 或 `$stock-kline` 后面**的文字是股票名称或代码。

## 你要做的

1. 读取并遵循 **stock-technical-analysis** skill
2. 拉取日 K、实时价，可选 MA
3. 输出趋势、支撑/压力、量价关系
4. 末尾加免责声明
