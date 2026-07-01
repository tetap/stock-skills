# 投资顾问流派手册

本文件为 `stock-investment-advisor` 的详细参考。分析时必须**先选定顾问 ID**，再按其框架解读数据，不得混用结论口径。

---

## 顾问一览

| ID | 名称 | 代表人物 | 核心命题 | 典型持有期 |
|----|------|----------|----------|------------|
| `graham` | 深度价值 | 本杰明·格雷厄姆、沃尔特·施洛斯 | 价格显著低于内在价值，安全边际 | 数月～数年（价值修复） |
| `buffett` | 质量价值 | 沃伦·巴菲特、查理·芒格 | 合理价格买入伟大公司 | 数年～数十年 |
| `fisher` | 成长投资 | 菲利普·费雪 | 少数高成长优质企业长期持有 | 数年～数十年 |
| `lynch` | GARP | 彼得·林奇 | 成长性与估值匹配（PEG） | 1～5 年 |
| `soros` | 宏观反身性 | 乔治·索罗斯 | 趋势、情绪与认知偏差自我强化 | 周～季度 |
| `dalio` | 宏观周期 | 瑞·达里奥 | 经济机器、债务周期、风险平衡 | 季度～年 |
| `composite` | 综合顾问 | 多流派融合 | 交叉验证，标注分歧点 | 视标的而定 |

列出顾问：用户输入 `list` 或 `列表` 时，输出上表并说明用法：`/stock buffett 贵州茅台` 或 `/stock 分析 贵州茅台`。

---

## 行业评估口径（A 股）

分析前先识别行业，切换估值权重（参考 [stockwise](https://github.com/cindylui479-create/stockwise) 思路）：

| Profile | 适用行业 | 估值侧重 |
|---------|----------|----------|
| `default` | 消费、制造、一般企业 | PE/PB、FCF Yield、盈利趋势 |
| `bank` | 银行 | PB、ROE÷PB 隐含回报、股息率、不良率趋势 |
| `insurance` | 保险 | PB、股息、净利稳定性 |
| `growth` | 营收 CAGR 高、研发驱动 | PEG、PS÷增速、毛利率趋势 |
| `cyclical` | 钢铁、煤炭、有色、航运、化工 | 周期位置、Shiller PE 思路、高股息防御 |

---

## 各流派：看什么数据

| 顾问 | 必拉工具 | 可选 |
|------|----------|------|
| 全部 | `resolve_symbol`, `get_realtime_quote` | — |
| graham | `get_financial_statements`(balance,income), `get_valuation_metrics` | `get_shareholders` |
| buffett | 同上 + `get_company_profile`, 3～5 年利润表 | `get_news_and_reports` |
| fisher | `get_financial_statements`(income), `get_company_profile` | `get_shareholders`, 行业对比 |
| lynch | `get_valuation_metrics`, `get_financial_statements`(income), `get_sector_detail` | PEG 手算 |
| soros | `get_indicator_interpretation`, `get_limit_up_gene`, `get_stock_fund_flow`, `get_major_events` | `get_kline`, 板块宏观 |
| dalio | `get_market_fund_flow`, `compare_performance`, `get_major_events` | 宏观新闻 |
| composite | 基本面+资金+事件+**均线(MA)+短线官方monitor** | 见 action-guide.md |

**所有分析类请求额外必拉**（见 [action-guide.md](action-guide.md)）：
`get_historical_series --indicators ma` · `get_kline --limit 20`

CLI 示例：

```bash
python scripts/em.py get_financial_statements --code 600519 --report-type income --limit 12
python scripts/em.py get_valuation_metrics --secid 1.600519
python scripts/em.py compare_performance --secid 1.600519 --benchmark-code 000300
```

---

## 流派详解

### `graham` 格雷厄姆 · 深度价值

**核心问题**：当前价是否显著低于保守估算的内在价值？

**关键检查**：
- Net-Net / 账面安全边际（流动资产 − 总负债 vs 市值）
- Graham Number ≈ √(22.5 × EPS × BVPS) 作 rough 参考
- 低 PB、低 PE，避免持续亏损
- 分散、不押单一叙事

**红旗**：价值陷阱（便宜因为基本面恶化）、会计异常、高负债

**输出立场**：`低估 / 合理 / 高估 / 数据不足`，不给「必买」

---

### `buffett` 巴菲特 · 质量价值

**核心问题**：这是否一门 10 年后仍大概率更强大的生意？价格是否合理？

**关键检查**：
- 护城河：品牌、成本、网络效应、切换成本（定性 + ROE 稳定性）
- 自由现金流倾向、低资本开支需求
- 管理层与资本配置（分红、回购、乱并购）
- 「合理价格」：不追极致便宜，拒绝平庸公司

**红旗**：ROE 靠杠杆堆高、一次性收益、行业颠覆

---

### `fisher` 费雪 · 成长投资

**核心问题**：未来 3～10 年销售与利润能否持续高于行业？

**关键检查**：
- 营收/净利润多年 CAGR
- 研发、产品管线、市场份额（定性）
- 管理层诚信与长期导向
- 容忍较高 PE，但不接受无增长的贵

**红旗**：成长靠并购堆叠、应收账款暴增、行业天花板

---

### `lynch` 林奇 · GARP

**核心问题**：成长是否已被价格反映？能否从生活中验证故事？

**关键检查**：
- **PEG = PE ÷ 盈利增长率**（增长率用一致口径，如近 3 年净利 CAGR）
  - PEG < 1：偏便宜（需验证成长可持续）
  - PEG ≈ 1：匹配
  - PEG > 1.5：偏贵
- 六类分类：slow growers / stalwarts / fast growers / cyclicals / turnarounds / asset plays
- 板块内相对排名

**红旗**：概念炒作、PEG 分母不可持续、散户叙事过热

---

### `soros` 索罗斯 · 反身性 / 趋势

**核心问题**：当前价格趋势与资金/叙事是否形成自我强化？拐点在哪？

**关键检查**：
- 价格趋势 + 量价 + 主力流向是否同向
- 事件 catalyst（政策、业绩、并购）
- 反身性：涨→叙事→更多买盘，或反之
- 明确止损/证伪条件（逻辑失效点）

**红旗**：纯情绪无基本面、流动性枯竭

**注意**：偏交易视角，持有期短，与价值流派结论可能相反——需标注

---

### `dalio` 达里奥 · 宏观周期

**核心问题**：该标的在 current 经济周期位置下风险收益比如何？

**关键检查**：
- 相对大盘/行业强弱（`compare_performance`）
- 板块顺周期 or 逆周期
- 杠杆、现金流在紧缩期的韧性
- 组合思维：单一标的结论需带「宏观情景」

**红旗**：宏观逆风行业的高 beta 裸奔

---

### `composite` 综合顾问

**流程**：
1. 分别用 graham / buffett / lynch / soros 视角交叉点评
2. 标注共识与分歧
3. **必须输出「近期操作建议」表**（见 action-guide.md），取多流派交集作为操作倾向

---

## 报告模板

**一律使用 [action-guide.md](action-guide.md) 增强模板**，含：
- 一句话结论 + **操作倾向**
- **近期操作建议**（看线周期、介入区间、确认/回避、观察期）
- 技术面快照（MA5/20/60）
- 基本面/事件/风险/流派分歧

旧版简模板已废弃，禁止只写 3 行摘要了事。

### 禁止

- 「必涨」「必买」「稳赚」
- 无数据支撑的精确目标价
- 隐瞒顾问风格导致的偏见

---

## 参考与致谢

流派梳理参考公开文献与社区实践，包括但不限于：
- 格雷厄姆《证券分析》/ 安全边际思想
- 费雪《怎样选择成长股》
- 巴菲特致股东信 / 芒格「合理价格买优秀公司」
- 林奇 PEG 与六类股票框架
- [stockwise](https://github.com/cindylui479-create/stockwise) 的行业 profile 分发思路
- [Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) 的多 preset 工作流表格式文档
