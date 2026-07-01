---
name: stock-technical-analysis
description: >-
  A 股技术面分析：K线、均线、趋势、量价。用于支撑压力、趋势判断、K线形态、技术指标。
---

# 技术面分析

## Workflow

1. `resolve_symbol --query "{标的}"`
2. `get_kline --secid {secid} --period daily --adjust qfq --limit 120`
3. `get_realtime_quote --secid {secid}`
4. 可选：`get_historical_series --secid {secid} --indicators ma --limit 120`
5. 可选：`get_stock_fund_flow --secid {secid} --limit 10`（量价背离）

## 输出模板

```markdown
# {名称} 技术面分析

## 趋势
- 短/中周期方向（上升/下降/震荡）

## 关键价位
- 支撑位 / 压力位（结合近期高低点与均线）

## 量价
- 放量/缩量，是否与价格方向一致

## 观察点
- 突破/跌破需关注的价位

> 仅供参考，不构成投资建议。
```

## 注意

- 长周期统计用 `stock-historical-analysis`，本 Skill 聚焦当前形态
