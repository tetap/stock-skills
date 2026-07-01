---
name: stock-analysis-orchestrator
description: >-
  A 股综合分析编排：基本面、技术面、资金面、筹码、历史、板块、事件一次性研究。
  用于全面分析、深入研究、值不值得关注某只股票。
---

# 综合分析编排

## 触发

用户要求「全面分析」「深入研究」「帮我看看 XX 值不值得关注」时使用。

## 标准流程

1. `resolve_symbol --query "{标的}"` → 得到 secid、code、name
2. 并行拉数（注意限流，分批执行）：
   - 基本面：`get_company_profile`, `get_financial_statements`, `get_valuation_metrics`
   - 技术面：`get_kline`, `get_historical_series --indicators ma`
   - 资金面：`get_stock_fund_flow`, `get_market_fund_flow`
   - 筹码：`get_chip_distribution`
   - 历史：`compare_performance --benchmark-code 000300`
   - 板块：从 profile 的 industry 查 `get_sector_overview` / `get_sector_detail`
   - 事件：`get_news_and_reports`, `get_shareholders`, `get_dragon_tiger`
3. 按下方章节合并输出

## 报告结构

```markdown
# {名称} 综合分析

## 1. 公司与板块定位
## 2. 历史表现（相对沪深300）
## 3. 技术面
## 4. 筹码结构
## 5. 资金面
## 6. 基本面与估值
## 7. 事件与舆情
## 8. 综合观点与风险
## 9. 免责声明
```

## 路由 shortcut

| 意图 | 转交 Skill |
|------|------------|
| 只问价格 | stock-quick-lookup |
| 只看 K 线 | stock-technical-analysis |
| 只看资金 | stock-capital-flow |
| 只看筹码 | stock-chip-analysis |
| 只看板块 | stock-sector-analysis |
| 指定投资流派 | stock-investment-advisor（配合 `/stock-role`） |

用户要求「按巴菲特/格雷厄姆/林奇方式分析」时，转交 **stock-investment-advisor**，不要套用本 Skill 的 neutral 综合报告结构。

## 合规

- 不给「必涨/必买」结论
- 末尾固定：**本分析仅供参考，不构成投资建议。**
