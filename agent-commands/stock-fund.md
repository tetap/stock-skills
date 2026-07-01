# 资金面分析（单维度）

用户在本条 `/stock-fund` **后面**的文字是股票名称或代码。

## 你要做的

1. 读取 **stock-capital-flow** skill
2. 近 20 日 `get_stock_fund_flow`，必要时 `get_fund_flow_rank` / `get_market_fund_flow`
3. 主力趋势、价量背离、市场/板块背景
4. 末尾免责声明

## 边界

- **仅资金面**，不走 review-protocol / §7
- 若问能不能买/全量分析 → **`/stock 分析 {标的}`**
