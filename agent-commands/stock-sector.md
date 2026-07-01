# 板块分析

用户在本条消息 `/stock-sector` **后面**的文字可能是：

- 板块名称，如 `半导体`、`银行`
- 或留空 / `今日` / `热点` → 分析今日涨幅靠前的行业板块
- **「走势 + 推荐几只 / 看好 / 龙头」** → 走 **sector-report.md**（C 流程）

## 你要做的

1. **选股/推荐** → stock-main + sector-report.md（≥12 次工具 + `get_review_protocol(flow=C)`）
2. **只看板块** → stock-sector-analysis + `get_sector_detail` / `get_sector_overview`
3. 新闻：`get_market_news`（可加 keyword）
4. 末尾免责声明
