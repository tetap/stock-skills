---
name: stock-analysis-orchestrator
description: >-
  A 股全量分析编排：基本面三表、估值、资金、筹码、技术、事件、板块。
  由 stock-main 分析流程调用；输出见 stock-main/analysis-report.md。
---

# 综合分析编排

## 触发

`/stock` 分析类请求、全面分析、值不值得关注、近期能否介入。

## 标准流程

1. `resolve_symbol` → secid、code、name
2. **全量拉数**（见 **stock-main/analysis-report.md** 工具表）：
   - 基本面：`get_company_profile`，`get_financial_statements` ×3（income/balance/cashflow），`get_valuation_metrics`，`get_shareholders`，`get_shareholder_count`
   - 技术：`get_kline`，`get_historical_series --indicators ma`，`compare_performance`，`get_indicator_interpretation`，`get_short_term_monitor`
   - 资金筹码：`get_stock_fund_flow`，`get_market_fund_flow`，`get_chip_distribution`
   - 事件板块：`get_major_events`，`get_news_and_reports`（news+announcement），`get_sector_detail`，`get_dragon_tiger`
3. 按 **stock-main/analysis-report.md** 输出（6 节，含近期操作）

## 路由

| 意图 | Skill |
|------|-------|
| 只问价格 | stock-quick-lookup |
| 全面/近期分析 | 本 Skill + stock-main |
| 只看资金/筹码/K线/板块 | 对应专项 Skill |

**不再使用** stock-investment-advisor / 顾问角色。

## 合规

不给必涨必买；末尾：**仅供参考，不构成投资建议。**
