# 全面分析（快捷别名）

等价于 **`/stock 分析 {标的}`**，走 **stock-main → composite 综合顾问** 一体化流程。

用户在本条消息 `/stock-analyze` **后面**的文字是标的或自然语言。

## 你要做的

1. 读取 **stock-main** skill，按「投资分析」意图执行（advisor_id = `composite`）
2. 按 composite 数据清单拉数，**stock-investment-advisor** 输出一份报告
3. **禁止**按基本面/技术面/资金面分工具章节堆砌
4. 末尾免责声明

主入口是 `/stock`；本命令仅为快捷方式。
