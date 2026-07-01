---
name: stock-sector-analysis
description: >-
  A 股板块分析：行业/概念涨跌、走势、资金、成分股、板块内选股。用于板块轮动、热点、龙头、推荐几只。
---

# 板块分析

主入口也可用 **`/stock 电池板块走势，推荐几只`**，模板见 **stock-main/sector-report.md**。

## Workflow

**定位板块（口语化）：**
```bash
python scripts/em.py search_sectors --query 电池 --limit 10
```

**板块排行：**
```bash
python scripts/em.py get_sector_overview --sector-type industry --limit 30
python scripts/em.py get_sector_overview --sector-type concept --limit 30
```

**板块详情：**
1. `get_sector_detail --board-name "{板块名}" --detail-type kline --limit 120`
2. `get_sector_detail --board-name "{板块名}" --detail-type fund_flow --limit 30`
3. `get_sector_detail --board-name "{板块名}" --detail-type members --limit 30`

**情绪：**
```bash
python scripts/em.py get_market_news --news-type flash --keyword 电池 --limit 15
```

**板块 + 选股：**
- 从 fund_flow/members 挑 3~5 只 → 每只 quote + 估值 + 资金 + news

## 场景路由

| 用户问题 | 工具 |
|----------|------|
| 今天什么板块涨得好 | get_sector_overview + get_market_news |
| XX 板块走势/推荐 | search_sectors + sector_detail + market_news + 轻量扫股 |
| XX 板块有哪些股票 | get_sector_detail(members) |
| 板块里资金最集中的票 | get_sector_detail(fund_flow) |

## 注意

- `board-name` 支持模糊匹配（如「电池」→「电池」概念板）；不确定时先 `search_sectors`
- 看好标的 ≠ 必买，须写理由与风险

