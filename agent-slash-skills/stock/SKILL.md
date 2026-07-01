---
name: stock
description: >-
  A 股主命令：查价、个股分析、板块走势选股、市场热点情绪。无投资顾问角色。
disable-model-invocation: true
argument-hint: "[查价 / 分析 / 板块 / 热点 + 内容]"
---

# A 股主命令

| 输入 | 行为 |
|------|------|
| `600519` / `贵州茅台` | 查现价 |
| `分析 XX` / `能不能买` | 个股全量分析 |
| `电池板块走势` / `推荐几只` | 板块 + 选股 → sector-report.md |
| `今天热点` / `情绪` | 市场简报 → market-brief.md |

## 必做

1. **stock-main** 路由 + 对应模板（analysis / sector / market-brief）
2. **新闻情绪必拉** `get_market_news`（flash，可加 keyword）
3. 简洁报告，禁止顾问角色、禁止只拉 2 个工具
