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
| `分析 XX` / `能不能买` | 个股全量分析（≥20 次工具 + 审核） |
| `电池板块走势` / `推荐几只` | 板块 + 选股 → sector-report.md |
| `今天热点` / `情绪` | 市场简报 → market-brief.md |

## 必做

1. **stock-main** 路由 + 对应模板（analysis / sector / market-brief）
2. 个股分析：**工具 ≥20 次** → `get_review_protocol(flow=B|C|D)` → review-protocol 门禁 → **7 节终稿（含 §7 审核纪要）**
3. **新闻情绪必拉** `get_market_news`（flash/headline，`source=all|eastmoney|sina`，可加 keyword）
4. 简洁报告，禁止顾问角色、禁止只拉 2 个工具
5. `quant_verdict` 为研究辅助，不等于 OOS 回测策略信号
