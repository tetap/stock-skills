# A 股分析报告模板

面向 **A 股市场**的综合分析，**不使用**格雷厄姆/巴菲特等顾问角色模块。先**尽量拉全数据**，再输出一份简洁、可操作的结论。

---

## 禁止

- 踢皮球（空泛「观望」、.redirect 其他命令、只贴 JSON）
- 投资顾问流派（buffett/graham/lynch 等）章节
- 「必涨 / 必买 / 稳赚 / 全仓」

---

## 分析必拉工具（分批执行，≥18 次，尽量全拉）

拿到 `secid`、`code` 后**逐条调用**下表每一行，缺项在报告中标注「未获取到 XX」：

**批次**：① 基本面 7 次 → ② 技术 6 次 → ③ 资金筹码 3 次 → ④ 事件板块 4~5 次

### 基本面（优先全部拉）

| 工具 | 参数 |
|------|------|
| `get_company_profile` | secid + code |
| `get_financial_statements` | code, income, limit 12 |
| `get_financial_statements` | code, balance, limit 8 |
| `get_financial_statements` | code, cashflow, limit 8 |
| `get_valuation_metrics` | secid |
| `get_shareholders` | code, limit 10 |
| `get_shareholder_count` | code, limit 8 |

### 行情与技术面

| 工具 | 参数 |
|------|------|
| `get_realtime_quote` | secid |
| `get_kline` | secid, limit 120 |
| `get_historical_series` | secid, limit 250, indicators=ma |
| `compare_performance` | secid, benchmark 000300 |
| `get_indicator_interpretation` | secid + code |
| `get_short_term_monitor` | code |

### 资金与筹码

| 工具 | 参数 |
|------|------|
| `get_stock_fund_flow` | secid, limit 20 |
| `get_market_fund_flow` | limit 10 |
| `get_chip_distribution` | secid, limit 60 |

### 事件与板块

| 工具 | 参数 |
|------|------|
| `get_major_events` | code, limit 15 |
| `get_news_and_reports` | code, news, limit 10, **source=all** |
| `get_news_and_reports` | code, announcement, limit 5 |
| `get_market_news` | flash, limit 20, **source=all**（东财+新浪+雪球热榜） |
| `get_market_news` | xueqiu_hot, limit 15, source=xueqiu |
| `get_market_news` | flash, keyword=行业词, limit 10 |
| `get_sector_detail` | 从 profile 行业名, members 或 fund_flow |
| `get_dragon_tiger` | code, limit 5（有则写，无则跳过） |

**§5 事件与板块** 必须写：个股新闻 2 条 + **与标的相关的市场热点/情绪** 1~2 条（来自 `get_market_news`）。

CLI 示例：

```bash
python scripts/em.py get_financial_statements --code 600519 --report-type income --limit 12
python scripts/em.py get_financial_statements --code 600519 --report-type balance --limit 8
python scripts/em.py get_financial_statements --code 600519 --report-type cashflow --limit 8
```

---

## 报告结构（简洁 · 可操作）

**篇幅**：全文控制在可读长度内；**表格填数 + 每节 1~3 句**，不要大段流派描述或重复贴工具原文。

```markdown
# {名称}（{代码}）分析

> 数据截止：{时间}

## 1. 结论与近期操作

**总判断**：{偏强|中性|偏弱|数据不足} · **操作倾向**：{可分批试探|等回调|持有观望|暂不介入|持有者减仓}

| 项目 | 内容 |
|------|------|
| 看线 | 日K + MA20（短线也看 MA5） |
| 关注/介入区间 | {价位或均线附近，有数写数} |
| 确认条件 | {如站稳 MA20、放量、财报后…} |
| 回避/止损参考 | {破 XX 转弱} |
| 观察期 | {5~20 日 / 1~3 月} |

2~3 句话说明**为什么**（基本面+趋势+资金各一句）。

## 2. 基本面与估值

| 指标 | 数值 | 说明 |
| PE/PB、市值 | | |
| 营收/净利趋势 | 近 4 季 | |
| 现金流 | 经营 CF | |
| 股东户数 | 最新变化 | |
| 估值结论 | | 贵/合理/便宜 |

## 3. 技术面

| MA5/20/60 | 现价位置 | 近 20 日高低 |
| 趋势 | 多头/空头/震荡 |
| 关键信号 | 指标解读摘要 1 条 |

## 4. 资金与筹码

| 主力近 5 日 | 大盘资金背景 | 获利比例/集中度 |

## 5. 事件与板块

- 大事提醒 2~3 条
- **情绪/热点**：与标的或所属行业相关的快讯 1~2 条
- 板块内相对位置（如有）
- 近期新闻/公告 1~2 条要点

## 6. 主要风险

- 2~4 条

> 仅供参考，不构成投资建议。
```

---

## 操作倾向用语

| 倾向 | 含义 |
|------|------|
| 可分批试探 | 质价趋势尚可，控制仓位 |
| 等回调 | 逻辑 OK 但价格或短期过热 |
| 持有观望 | 已持有观察；未持有不新建仓 |
| 暂不介入 | 基本面或趋势明显偏弱 |
| 持有者减仓 | 估值或趋势显著恶化 |
