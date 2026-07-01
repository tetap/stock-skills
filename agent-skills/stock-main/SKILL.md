---
name: stock-main
description: >-
  A 股主命令编排：/stock 统一入口。自动识别查价 vs 投资分析，按投资顾问流派拉取对应指标并输出一体化顾问报告。
  用于 /stock、$stock 及自然语言股票研究请求。
---

# 主命令编排（/stock）

**原则**：用户只面对一个入口 `/stock`。Agent **先理解意图 → 选顾问 → 按顾问指标拉数 → 顾问一体化解读**，禁止把多个子 Skill 的结果分段堆砌。

## 意图路由

解析 `/stock` 或 `$stock` **后面整段自然语言**：

| 意图 | 触发信号 | 动作 |
|------|----------|------|
| **A. 查现价** | 仅代码/名称，或含「多少钱、现价、涨多少、报价」且**无**分析诉求 | → **stock-quick-lookup**，简短表格，结束 |
| **B. 投资分析** | 含「分析、投资建议、值不值得、怎么看、能不能买、近期、研究、评估、建议、推断」等 | → 本 Skill **C 流程** |
| **C. 指定顾问** | 含顾问 ID/中文名（见下表） | → **C 流程**，锁定顾问 |
| **D. 列出顾问** | `list` / `列表` / `有哪些顾问` | → 输出 advisors 一览表 |

**默认**：有分析诉求但未指定顾问 → `composite`（综合顾问）。

### 顾问 ID 识别

| 关键词 | advisor_id |
|--------|------------|
| 格雷厄姆、graham、深度价值 | graham |
| 巴菲特、buffett、芒格 | buffett |
| 费雪、fisher、成长 | fisher |
| 林奇、lynch、GARP、PEG | lynch |
| 索罗斯、soros、趋势、反身 | soros |
| 达里奥、dalio、宏观周期 | dalio |
| （未匹配） | composite |

从文本中**剥离**顾问关键词后，剩余部分提取股票名称或代码。

---

## C 流程：顾问一体化分析（核心）

这是 `/stock` 的主能力，**替代**分散调用 `/stock-analyze`、`/stock-fund` 等子命令的默认用法。

### 步骤 1 — 解析

1. 提取 `advisor_id`（默认 `composite`）与 `{标的}`
2. 若标的为空 → 提示：`/stock 分析 贵州茅台` 或 `/stock buffett 600519`

### 步骤 2 — 按顾问拉数（只拉需要的，分批限流）

**必读** [stock-investment-advisor/advisors.md](advisors.md)「各流派：看什么数据」。

执行顺序（通用）：

1. `resolve_symbol` → secid、code、name
2. `get_realtime_quote`
3. 按 advisor_id 拉**该顾问必拉 + 合理可选**工具（勿全量 19 工具除非 composite）

`composite` 综合顾问拉数清单（一体化，非分工具输出）：

| 维度 | 工具 |
|------|------|
| 基本面 | `get_company_profile`, `get_financial_statements`(income, limit 12), `get_valuation_metrics` |
| 相对表现 | `compare_performance --benchmark-code 000300` |
| 资金/情绪 | `get_stock_fund_flow`, `get_market_fund_flow` |
| 技术概览 | `get_kline --limit 60`（只提炼趋势，不贴全量 K 线） |
| 事件 | `get_news_and_reports --limit 5` |

其他 advisor 严格按 advisors.md 表格，**不得**为凑章节额外拉筹码/龙虎榜等无关数据。

数据来源：优先 MCP `eastmoney-stock`，否则 `python scripts/em.py`。禁止编造。

### 步骤 3 — 行业 profile

根据 `get_company_profile.industry` 选用：`bank` / `insurance` / `growth` / `cyclical` / `default`（见 advisors.md）。

### 步骤 4 — 顾问解读（唯一输出主体）

**读取并遵循 stock-investment-advisor**，按 [advisors.md](advisors.md) 报告模板输出**一份**连贯报告：

```markdown
# {名称} · {顾问名}视角

> 数据截止：… | 顾问：{id}

## 顾问结论（3 行内）
立场：低估 / 合理 / 高估 / 观望 / 数据不足
近期关注点：…

## 关键依据（顾问关心的指标，一张表）
| 指标 | 数值 | 顾问如何解读 |
| … | … | … |

## 支持观点
- …

## 风险与红旗
- …

## 数据缺口（如有）
- …

## 与其他流派的分歧（composite 必填）
- …

> 本分析采用 {顾问名} 风格框架，仅供参考，不构成投资建议。
```

### 输出禁令（重要）

- **禁止**按工具分节：`## 资金面`、`## 筹码` 各贴一段原始数据
- **禁止**「下面调用 stock-fund / stock-chip …」式流程说明
- **禁止**「必涨 / 必买 / 稳赚」
- 原始数据只进入「关键依据」表或括号引用，**主体必须是顾问语言**

---

## 与子命令关系

| 子命令 | 定位 |
|--------|------|
| `/stock` | **主入口**（本 Skill） |
| `/stock-analyze` | 等价于 `/stock 分析 {标的}`（composite） |
| `/stock-role` | 等价于 `/stock {advisor_id} {标的}` |
| `/stock-fund` 等 | 仅当用户**明确**「只看资金/筹码/K线」时使用 |

用户说「分析一下 / 投资建议」时，**不要**引导去 `/stock-analyze`，直接走 C 流程。

---

## 示例

**输入**：`/stock 帮我分析一下贵州茅台，推断近期投资建议`

1. 意图 B → advisor `composite`，标的贵州茅台
2. 拉 composite 清单数据
3. 输出综合顾问一体化报告（多流派交叉，非工具拼接）

**输入**：`/stock buffett 宁德时代`

1. 意图 C → `buffett`，标的宁德时代
2. 只拉 buffett 必拉工具
3. 巴菲特视角单报告

**输入**：`/stock 600519`

1. 意图 A → 现价表格
