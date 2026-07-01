# 市场热点与情绪简报（专业 · 有立场）

用于 `/stock 今天什么热点` / `最近情绪怎么样` 等 **无单一标的** 请求。

---

## 写作标准

- §1 必须是 **可验证的判断**：「情绪偏热但结构分化」优于「市场有热点」
- 每个热点主题写 **驱动因素 + 受益板块 + 持续性（1 日/1 周/更长）**
- 「可关注方向」改为 **「今日主线排序」**，给 2~4 条带优先级的主题，不是泛泛列表
- 必须交叉：快讯 + 板块涨幅 + 资金净流入 + 雪球讨论热榜

---

## 必拉工具

| 工具 | 参数 |
|------|------|
| `get_market_news` | flash, limit 30, source=all |
| `get_market_news` | headline, limit 15 |
| `get_market_news` | xueqiu_hot, limit 15, source=xueqiu |
| `get_sector_overview` | concept, limit 15 |
| `get_sector_overview` | industry, limit 15 |
| `get_market_fund_flow` | limit 10 |
| `get_fund_flow_rank` | limit 15 |
| `get_market_snapshot` | change_pct, limit 10 |

若用户提到主题，追加 keyword 快讯 + `search_sectors` + 板块 K 线。

---

## 报告结构

```markdown
# 市场热点与情绪

> 数据截止：{时间} · 整体情绪：**{偏热|偏冷|结构性分化}** · 置信度：**{X}/10**

## 1. 一句话结论

{今日/近期主线 + 最大风险，如「锂电并购线活跃但指数缩量，追高风险大」}

## 2. 主线排序（2~4 条，按优先级）

| 优先级 | 主题 | 驱动（新闻/政策） | 受益板块 | 资金是否配合 | 持续性 |
|--------|------|-------------------|----------|--------------|--------|

## 3. 热点快讯（5~8 条）

| 时间 | 标题 | 影响判断（1 句，带方向） |

## 4. 板块与资金

| 概念 Top5 | 行业 Top5 | 主力净流入方向 | 雪球讨论 Top3 |

## 5. 策略提示

- **可跟踪**：{什么条件下可以参与}
- **回避**：{什么信号出现应停手}

## 6. 风险

- 2~4 条具体风险（非套话）

## 7. 审核纪要

| 轮次 | 质疑 | 结论 |
| R3 | 热点是否一日游 | … |
| R4 | 新闻 vs 板块 vs 资金 | … |

> 仅供参考，不构成投资建议。
```

输出前调用 `get_review_protocol(flow=D)`，执行 [review-protocol.md](review-protocol.md) **D 流程三轮**。

---

## 与个股分析的关系

追问某只股票 → **analysis-report.md** 全量分析。  
问板块+选股 → **sector-report.md**。
