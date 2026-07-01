---
name: stock-role
description: >-
  /stock-role 是 /stock 的快捷别名：指定投资顾问流派分析。手动调用时使用。
disable-model-invocation: true
argument-hint: "[顾问ID] [股票名称或代码] 或 list"
---

# 投资顾问（快捷别名）

等价于 **`/stock {顾问ID} {股票}`** → **stock-main** 顾问流程。

## 你要做的

1. 读取 **stock-main** skill
2. `list` → 顾问一览；否则解析 advisor_id + 标的
3. 按 stock-investment-advisor / advisors.md 拉数并输出**一份**报告
4. 主入口是 `/stock`
