# 市场热点与情绪简报

用于 `/stock 今天什么热点` / `最近情绪怎么样` / `哪些板块在动` 等 **无单一标的** 的请求。

---

## 必拉工具

| 工具 | 参数 |
|------|------|
| `get_market_news` | flash, limit 30 |
| `get_market_news` | headline, limit 15 |
| `get_market_news` | breakfast, limit 3（若有当日） |
| `get_sector_overview` | concept, limit 15 |
| `get_sector_overview` | industry, limit 15 |
| `get_market_fund_flow` | limit 10 |
| `get_fund_flow_rank` | limit 15 |
| `get_market_snapshot` | change_pct, limit 10 |

若用户提到主题（如「电池」），追加：

| 工具 | 参数 |
|------|------|
| `get_market_news` | flash, keyword=主题 |
| `search_sectors` + `get_sector_detail` kline | 该主题板块走势 |

---

## 报告结构（简洁）

```markdown
# 市场热点与情绪

> 数据截止：{时间}

## 1. 一句话

今日/近期市场 **情绪偏{热|冷|分化}**，主线在 {板块/主题}。

## 2. 热点快讯（5~8 条）

| 时间 | 标题 | 关联 |
| 对 A 股/板块的可能影响（各 1 句） |

## 3. 强势板块

| 概念 Top5 | 行业 Top5 | 资金净流入方向 |

## 4. 可关注方向（非必买）

- 2~4 个 **主题 + 理由**（新闻+资金+板块涨幅交叉）

## 5. 风险

- 追高风险、政策变化、外围波动等

> 仅供参考，不构成投资建议。
```

---

## 与个股分析的关系

用户若在热点简报后追问某只股票 → 切 **analysis-report.md** 全量分析。

用户若问某板块走势+选股 → 切 **sector-report.md**。
