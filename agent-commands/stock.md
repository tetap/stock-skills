# A 股主命令

用户在本条 `/stock` 后面输入：查价、**个股分析**、**板块走势/选股**、**市场热点/情绪** 等。

## 示例

```
/stock 600519
/stock 分析 黔源电力，看几日线能不能介入
/stock 电池板块最近走势，给我几个看好的股票
/stock 今天有什么热点，情绪怎么样
```

## 你要做的

1. **stock-main** 按意图路由：
   - 查价 → quick-lookup
   - 个股 → analysis-report.md（≥18 次工具）
   - 板块+选股 → sector-report.md（≥12 次 + 候选股轻扫）
   - 热点/情绪 → market-brief.md
2. **新闻情绪必拉**：`get_market_news`（flash/headline，可加 keyword）
3. 输出简洁报告（表格为主），§1 给可操作建议；**禁止顾问角色**
4. 末尾免责声明
