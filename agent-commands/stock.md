# A 股主命令

用户在本条消息 `/stock` **后面**的整段文字是自然语言请求（查价、分析、指定顾问均可）。

## 示例

```
/stock 贵州茅台                          → 查现价
/stock 帮我分析一下贵州茅台，给近期投资建议  → 综合顾问一体化分析
/stock buffett 宁德时代                   → 巴菲特视角分析
/stock list                              → 列出投资顾问流派
```

## 你要做的

1. **读取并遵循 stock-main skill**（主编排，唯一入口逻辑）
2. 按 stock-main 意图路由：
   - 仅查价 → stock-quick-lookup
   - 分析/建议/值不值得 → 按顾问拉数 → stock-investment-advisor 一体化报告
   - list → 顾问一览表
3. 数据：优先 MCP `eastmoney-stock`，否则 `python scripts/em.py`
4. **禁止**把多个子工具结果分段堆砌；输出必须是**一份顾问报告**
5. 末尾免责声明

子命令 `/stock-analyze`、`/stock-role` 是快捷别名，用户在本条已用 `/stock` 时不要.redirect 到其他命令。
