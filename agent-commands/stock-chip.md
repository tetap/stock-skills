# 筹码分析（单维度）

用户在本条 `/stock-chip` **后面**的文字是股票名称或代码。

## 你要做的

1. 读取 **stock-chip-analysis** skill
2. `get_chip_distribution`、现价、可选 K 线
3. 成本区、集中度、现价位置
4. 末尾免责声明

## 边界

- **仅筹码**，不走 review-protocol
- 全量/能不能买 → **`/stock 分析 {标的}`**
