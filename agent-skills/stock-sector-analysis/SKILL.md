---
name: stock-sector-analysis
description: >-
  A 股板块分析：行业/概念涨跌排名、成分股、板块K线、板块内龙头。用于行业轮动、概念热点、板块龙头、哪个板块强。
---

# 板块分析

## Workflow

**板块排行：**
```bash
python scripts/em.py get_sector_overview --sector-type industry --limit 30
python scripts/em.py get_sector_overview --sector-type concept --limit 30
```

**板块详情：**
1. `get_sector_detail --board-name "{板块名}" --sector-type industry --detail-type members`
2. `get_sector_detail --board-name "{板块名}" --detail-type kline --limit 120`
3. `get_sector_detail --board-name "{板块名}" --detail-type fund_flow --limit 30`

**板块 + 个股：**
- 从 members 取龙头，再 `resolve_symbol` + `get_realtime_quote`

## 场景路由

| 用户问题 | 工具 |
|----------|------|
| 今天什么板块涨得好 | get_sector_overview |
| XX 板块有哪些股票 | get_sector_detail(members) |
| XX 板块近3个月走势 | get_sector_detail(kline) |
| XX 板块里资金最集中的票 | get_sector_detail(fund_flow) |

## 输出模板

```markdown
# {板块名} 板块分析

## 板块表现
- 涨跌幅、上涨/下跌家数、领涨股

## 成分股
- Top 成分股列表

## 走势
- 板块指数近期趋势（若有 K 线）

> 仅供参考，不构成投资建议。
```

## 注意

- `board-name` 需与东方财富板块名精确匹配；不确定时先从 overview 列表确认
