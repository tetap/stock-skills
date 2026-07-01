---
name: stock-capital-flow
description: >-
  A 股资金面分析：主力净流入、个股资金排名、大盘资金背景、板块资金。用于主力、净流入、资金流、热点板块资金。
---

# 资金面分析

## Workflow

**个股：**
1. `resolve_symbol --query "{标的}"`
2. `get_stock_fund_flow --secid {secid} --limit 20`
3. `get_fund_flow_rank --limit 50`（找全市场排名）
4. `get_market_fund_flow --limit 10`（大盘背景）

**板块热点：**
1. `get_sector_overview --sector-type industry --sort change_pct --limit 20`
2. 对目标板块 `get_sector_detail --board-name "{板块}" --detail-type fund_flow`

## 输出模板

```markdown
# {名称} 资金面分析

## 个股资金
- 近5日主力净流入趋势
- 与股价：同步 / 背离

## 市场对比
- 全市场资金排名（若可估算）

## 大盘背景
- 近期大盘主力流向

## 板块背景
- 所属行业资金表现

> 仅供参考，不构成投资建议。
```

## 解读

- 连续多日主力净流入 + 价涨：资金推动偏强
- 价涨但主力净流出：警惕背离
- 北向等数据若接口不可用，明确说明而非猜测
