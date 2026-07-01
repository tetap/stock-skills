---
name: stock-fundamental-analysis
description: >-
  A 股基本面分析：公司简介、三大财报、估值指标、股东结构。用于估值、盈利能力、负债、分红、财报分析。
---

# 基本面分析

## Workflow

1. `resolve_symbol --query "{标的}"`
2. `get_company_profile --secid {secid} --code {code}`
3. `get_financial_statements --code {code} --report-type income --limit 8`
4. 可选：`--report-type balance` / `cashflow`
5. `get_valuation_metrics --secid {secid}`
6. 可选：`get_shareholders --code {code}`

## 输出模板

```markdown
# {名称} 基本面分析

## 公司概况
- 行业 / 主营业务 / 上市日期

## 财务趋势
- 营收、净利润近几期变化
- 毛利率、负债率等关键变化

## 估值
- PE / PB / 总市值

## 风险点
- 业绩下滑、高负债、股东减持等

> 仅供参考，不构成投资建议。
```

## 解读要点

- 对比至少 4 个报告期，避免单期误判
- 估值需结合行业，勿孤立看 PE
