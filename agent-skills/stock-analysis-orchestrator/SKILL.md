---
name: stock-analysis-orchestrator
description: >-
  A 股全量分析编排：基本面三表、估值、资金、筹码、技术、事件、板块。
  由 stock-main 分析流程调用；输出见 stock-main/analysis-report.md。
---

# 综合分析编排

## 触发

`/stock` 分析类请求、板块走势选股、市场热点情绪、值不值得关注、近期能否介入。

## 标准流程

### 个股

1. `resolve_symbol` → secid、code、name
2. **全量拉数**（见 **stock-main/analysis-report.md**），含 `get_market_news`
3. `get_review_protocol(flow=B)` → 按 review-protocol 审核 → 6 节报告 + §7 审核纪要

### 板块 + 选股

见 **stock-main/sector-report.md**：`search_sectors` → 板块 kline/资金/成分 → 快讯 keyword → 3~5 只轻扫

### 市场热点

见 **stock-main/market-brief.md**：快讯 + 板块排行 + 资金

## 路由

| 意图 | Skill |
|------|-------|
| 只问价格 | stock-quick-lookup |
| 全面/近期分析 | 本 Skill + stock-main |
| 只看资金/筹码/K线/板块 | 对应专项 Skill |

**不再使用** stock-investment-advisor / 顾问角色。

## 何时转交

| 场景 | 入口 |
|------|------|
| 单维度（仅资金/筹码/K线/基本面） | 对应专项 Skill + `/stock-*` 命令 |
| 个股全量 + 审核 | **stock-main** B 流程 |
| 板块选股 | sector-report C 流程 |
| 市场热点 | market-brief / `/stock-market` D 流程 |

## 合规

不给必涨必买；末尾：**仅供参考，不构成投资建议。**
