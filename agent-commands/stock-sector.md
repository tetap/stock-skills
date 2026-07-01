# 板块分析

用户在本条消息 `/stock-sector` **后面**的文字可能是：

- 板块名称，如 `半导体`、`银行`
- 或留空 / `今日` / `热点` → 分析今日涨幅靠前的行业板块

## 你要做的

1. 读取并遵循 **stock-sector-analysis** skill
2. 若指定板块名：`get_sector_detail`（members + fund_flow）
3. 若未指定：`get_sector_overview --sector-type industry --limit 15`
4. 末尾加免责声明
