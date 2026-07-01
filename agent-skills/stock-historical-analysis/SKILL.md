---
name: stock-historical-analysis
description: >-
  A 股历史数据分析：区间涨跌幅、最大回撤、波动率、相对沪深300强弱。用于近一年表现、历史涨跌、和指数对比、回撤分析。
---

# 历史数据分析

## Workflow

1. `resolve_symbol --query "{标的}"`
2. `get_historical_series --secid {secid} --limit 250 --indicators ma`
3. `compare_performance --secid {secid} --benchmark-code 000300 --limit 250`
4. 可选：换 `--benchmark-code 000001`（上证）或同行业龙头 secid

## 输出模板

```markdown
# {名称} 历史表现

| 指标 | 个股 | 基准(沪深300) |
|------|------|---------------|
| 区间涨跌幅 | | |
| 最大回撤 | | |
| 年化波动 | | |
| 相对强弱 | | |

## 结论
- 跑赢/跑输基准的原因简述（结合行业与大盘）

> 仅供参考，不构成投资建议。
```

## 与技术面的区别

- 本 Skill：长周期统计与相对表现
- `stock-technical-analysis`：当前形态与买卖点
