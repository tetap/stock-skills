# 市场热点 / 情绪简报

用户在本条消息 `/stock-market` **后面**的文字是热点/情绪相关描述，可留空。

示例：`/stock-market 今天有什么热点` · `/stock-market 情绪怎么样`

等价于 **`/stock 今天有什么热点`** → **market-brief.md**（D 流程）。

## 你要做的

1. **stock-main** D 流程 + [market-brief.md](../agent-skills/stock-main/market-brief.md)
2. 拉快讯/板块排行/资金（见模板工具表）
3. `get_review_protocol(flow=D)` → 输出含审核纪要的简报
4. 末尾免责声明

## 与专项命令的区别

| 命令 | 用途 |
|------|------|
| `/stock-market` | 全市场热点/情绪（无单一标的） |
| `/stock-news` | 单股事件/舆情 |
| `/stock 分析` | 个股全量分析 |
