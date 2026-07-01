---
name: stock-analyze
description: >-
  /stock-analyze 是 /stock 的快捷别名：综合顾问一体化分析。手动调用时使用。
disable-model-invocation: true
argument-hint: "[股票名称或代码]"
---

# 全面分析（快捷别名）

等价于 **`/stock 分析 {标的}`** → **stock-main**（composite 综合顾问）。

## 你要做的

1. 读取 **stock-main** skill，投资分析意图，`advisor_id = composite`
2. 按 composite 清单拉数 → **stock-investment-advisor** 一份报告
3. 禁止分工具章节堆砌；主入口是 `/stock`
