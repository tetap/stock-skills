---
name: stock-investment-advisor
description: >-
  以经典投资流派（格雷厄姆、巴菲特、费雪、林奇、索罗斯、达里奥等）解读 A 股数据并给出风格化观点。
  配合 /stock-role 或用户指定顾问 ID 使用。用于价值投资、成长、GARP、宏观、顾问视角分析。
---

# 投资顾问分析

## 何时使用

- 用户通过 **`/stock` 主命令**发起分析（默认路径）
- 用户调用 `/stock-role`、`$stock-role` 或指定顾问流派
- 用户问「按巴菲特/格雷厄姆/林奇的方式看 XX」
- 需要**风格化**研究结论，而非纯数据 dump

**由 stock-main 调用**：只负责「顾问解读」；数据拉取清单见 advisors.md，输出必须一体化，禁止按工具分节。

## 第一步：确定顾问

从用户输入解析 `advisor_id` 与标的：

| 输入示例 | advisor_id | 标的 |
|----------|------------|------|
| `buffett 贵州茅台` | buffett | 贵州茅台 |
| `600519` | composite（默认） | 600519 |
| `list` / `列表` | — | 输出顾问表 |

合法 ID：`graham` `buffett` `fisher` `lynch` `soros` `dalio` `composite`

详细流派定义见 [advisors.md](advisors.md)。

## 第二步：拉取数据

1. `resolve_symbol` → secid、code
2. 按 [advisors.md](advisors.md)「看什么数据」表调用 MCP 或 `python scripts/em.py`
3. **禁止编造**；缺数据则写「数据不足」并列出缺失项

## 第三步：行业 profile

根据 `get_company_profile` 的 industry 选择评估口径：`bank` / `insurance` / `growth` / `cyclical` / `default`

## 第四步：按流派输出

严格使用 [advisors.md](advisors.md) 报告模板与「禁止」条款。

- 结论用：`低估 / 合理 / 高估 / 观望 / 数据不足`（不用「强烈买入」）
- composite 必须包含多流派交叉对比
- soros / dalio 偏宏观与趋势，与 graham 结论冲突时**显式说明**

## 与其他 Skill 关系

| Skill | 关系 |
|-------|------|
| stock-analysis-orchestrator | composite 可复用其数据拉取清单 |
| stock-fundamental-analysis | graham/buffett/fisher/lynch 可复用 |
| stock-capital-flow | soros 必用 |
| stock-quick-lookup | 仅查价时不要用本 Skill |

## 合规

末尾固定：**本分析采用 {顾问名} 风格框架，仅供参考，不构成投资建议。**
