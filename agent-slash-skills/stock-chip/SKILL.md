---
name: stock-chip
description: >-
  A 股筹码集中度分析。手动调用 /stock-chip 或 $stock-chip。
disable-model-invocation: true
argument-hint: "[股票名称或代码]"
---

# 筹码分析

用户在本条消息 **`/stock-chip` 或 `$stock-chip` 后面**的文字是股票名称或代码。

## 你要做的

1. 读取并遵循 **stock-chip-analysis** skill
2. 拉取筹码分布、现价与 K 线
3. 输出成本区、集中度、现价相对位置
4. 末尾加免责声明
