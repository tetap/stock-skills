# 投资顾问（快捷别名）

等价于 **`/stock {顾问ID} {股票}`**，走 **stock-main** 顾问分析流程。

用户在本条消息 `/stock-role` **后面**的文字：`[顾问ID] [股票]` 或 `list`。

## 示例

- `/stock-role buffett 贵州茅台` → 同 `/stock buffett 贵州茅台`
- `/stock-role list` → 同 `/stock list`

## 你要做的

1. 读取 **stock-main** skill（勿单独走分散子工具）
2. 解析顾问 ID 与标的，按 advisors.md 拉数 → 一体化顾问报告
3. 末尾免责声明

主入口是 `/stock`；本命令仅为指定顾问的快捷方式。
