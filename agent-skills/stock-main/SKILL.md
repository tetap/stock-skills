---
name: stock-main
description: >-
  A 股 /stock 主命令：查价或全量数据分析。分析时拉齐基本面/技术面/资金/筹码/事件，
  输出简洁可操作建议，不使用投资顾问角色模块。
---

# 主命令编排（/stock）

**原则**：一个入口 `/stock`。分析时 **先尽量拉全数据 → 再写一份简洁报告**，禁止踢皮球、禁止顾问角色。

## 意图路由

| 意图 | 触发 | 动作 |
|------|------|------|
| 查现价 | 仅代码/名称，或「多少钱、现价」且无分析词 | → **stock-quick-lookup** |
| **分析** | 分析、投资建议、能不能买、值不值得、看几日线、近期 等 | → **B 流程** |
| list | 用户问 list/列表 | → 说明：`/stock 分析 股票名`（已无顾问 list） |

**不再使用** buffett/graham/lynch 等顾问 ID；若用户提到，忽略角色，走 B 流程。

---

## B 流程：全量分析

### 1. 解析标的

`resolve_symbol` → secid、code、name

### 2. 拉数（核心：尽量全拉，≥18 次工具调用）

**必读** [analysis-report.md](analysis-report.md)「分析必拉工具」表。

按批次执行（限流 ≥0.6s），顺序建议：

1. **基本面全套**（7 次）：profile + income/balance/cashflow + 估值 + 股东 + 股东户数
2. **行情技术**（6 次）：quote + kline 120 + historical_series(ma) 250 + compare + indicator + short_term_monitor
3. **资金筹码**（3 次）：stock_fund_flow + market_fund_flow + chip_distribution
4. **事件板块**（4~5 次）：major_events + news + announcement + sector_detail + dragon_tiger

**自检**：写报告前确认已调用上表全部行；少于 18 次视为未完成分析。

**禁止**只拉 quote + 一条 kline 就写报告。基本面三张报表必须尝试。

缺数据：报告中写「未获取到 XX」，不要编造。

### 3. 输出

按 [analysis-report.md](analysis-report.md) 模板，**6 个章节**，重点在 **§1 结论与近期操作**（看几日线、能否介入、价位条件）。

### 输出禁令

- 禁止投资顾问/流派章节
- 禁止按工具名分段贴原始 JSON
- 禁止 redirect `/stock-analyze` 等
- 禁止必涨必买

---

## 与子命令

| 命令 | 说明 |
|------|------|
| `/stock` | 主入口 |
| `/stock-analyze` | 同 `/stock 分析 {标的}` |
| `/stock-role` | **已废弃**，同全量分析，忽略顾问参数 |
| `/stock-fund` 等 | 仅用户明确单一维度时使用 |

---

## 示例

`/stock 分析 黔源电力，看几日线能不能买`

1. 拉 analysis-report.md 所列全部工具
2. 输出 6 节报告，§1 含 MA、介入区间、操作倾向
