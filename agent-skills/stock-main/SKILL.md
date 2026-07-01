---
name: stock-main
description: >-
  A 股 /stock 主命令：查价、个股全量分析、板块走势选股、市场热点情绪。
  分析时拉齐数据并经多重审核（审计/质疑/测试/门禁）后输出高置信报告。
---

# 主命令编排（/stock）

**原则**：一个入口 `/stock`。先 **尽量拉全数据** → **多重审核**（见 [review-protocol.md](review-protocol.md)）→ 再输出 **带 §7 审核纪要** 的终稿。

编排总览：[AGENTS.md](../../AGENTS.md)

## 报告风格（重要）

- **专业**：每个判断锚定数据；四维度交叉；相对沪深300与板块强弱。
- **大胆**：§1 评级 + 置信度 + 具体买卖区间；**终稿置信度 ≥7 才可强立场**。
- **可审计**：终稿必须含 **§7 审核纪要**（R2~R5 质疑与修订摘要）。
- 禁止一遍过稿；禁止初稿置信度 >6。

## 意图路由

| 意图 | 触发 | 动作 |
|------|------|------|
| 查现价 | 仅代码/名称，或「多少钱、现价」且无分析词 | → **stock-quick-lookup** |
| **个股分析** | 分析某**具体股票**、能不能买、看几日线 | → **B 流程** |
| **板块/选股** | 板块、行业、概念 + 走势/看好/推荐/龙头/有哪些票 | → **C 流程** |
| **热点/情绪** | 热点、情绪、今天什么板块、市场怎么样、新闻 | → **D 流程** |
| list | list/列表 | → 说明：`/stock 分析 股票名` |

**不再使用** buffett/graham/lynch 等顾问 ID。

---

## B 流程：个股全量分析

1. `resolve_symbol` → secid、code、name
2. 拉数 ≥ **20 次**，见 [analysis-report.md](analysis-report.md)（含 `get_quant_technical`、新闻/情绪）
3. 调用 `get_review_protocol(flow=B)` 获取轮次清单，执行 [review-protocol.md](review-protocol.md) **R1~R6**
4. 输出 **7 节终稿**（§1~§6 报告 + **§7 审核纪要**）；§1 含评级、终稿置信度、交易计划

`quant_verdict` / Alpha158/360 为**研究辅助**，不等于通过 OOS 回测的策略信号。

子 Skill：**stock-report-review**（审核清单速查）

---

## C 流程：板块走势 + 选股

**示例**：`/stock 帮我看看电池板块最近的走势，给我几个你看好的股票`

1. 读 [sector-report.md](sector-report.md)
2. `search_sectors("电池")` → 选定板块
3. 拉板块 K 线、资金、成分股 + **市场快讯/要闻（带 keyword）**
4. 对 3~5 只候选做轻量扫描（现价、估值、资金、新闻）
5. 输出板块报告 + 首选标的表；过 [review-protocol.md](review-protocol.md) **C 流程四轮** + §7 审核纪要

---

## D 流程：市场热点与情绪

**示例**：`/stock 今天有什么热点` / `最近情绪面怎么样`

1. 读 [market-brief.md](market-brief.md)
2. 拉 7×24 快讯、要闻、板块排行、大盘/个股资金
3. 交叉提炼主线；过 [review-protocol.md](review-protocol.md) **D 流程三轮** + 审核纪要

**雪球帖子/热门资讯**：先 `get_xueqiu_auth_status`；若 `authenticated: false` 或返回 `interrupt` → 提示用户在 Chrome/Safari 打开 https://xueqiu.com/hq 登录（自动读 Cookie，**无需**手动复制 token，除非 MCP 权限导致持续失败）。

---

## 输出禁令

- 禁止投资顾问/流派章节
- 禁止只拉 2 个工具就写报告
- 禁止 redirect 其他命令
- 禁止必涨必买
- 禁止跳过 review-protocol 直接交终稿
- 禁止无 §7 审核纪要的个股/板块报告

---

## 与子命令

| 命令 | 说明 |
|------|------|
| `/stock` | 主入口（查价 / 个股 / 板块 / 热点） |
| `/stock-analyze` | 同 `/stock 分析 {标的}` |
| `/stock-sector` | 可单独用，逻辑同 C 流程 |
| `/stock-news` | 可单独查事件，分析时仍须拉新闻 |

---

## 示例

```
/stock 分析 黔源电力，看几日线能不能买
/stock 电池板块最近走势，推荐几只
/stock 今天市场有什么热点
```
