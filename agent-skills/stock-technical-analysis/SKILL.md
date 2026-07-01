---
name: stock-technical-analysis
description: >-
  A 股技术面分析：K线、均线、趋势、量价。用于支撑压力、趋势判断、K线形态、技术指标。
---

# 技术面分析

## 何时转交 stock-main

| 用户意图 | 转交 |
|----------|------|
| 能不能买 / 看几日线 / 全量 | **`/stock 分析 {标的}`** |
| 仅看趋势、支撑压力 | **本 Skill**（`/stock-kline`） |

`get_quant_technical` 可在本 Skill 使用，但 **quant 非策略信号**；全量报告仍走 stock-main。

## Workflow

1. `resolve_symbol --query "{标的}"`
2. `get_kline --secid {secid} --period daily --adjust qfq --limit 120`
3. `get_realtime_quote --secid {secid}`
4. 可选：`get_historical_series --secid {secid} --indicators ma --limit 120`
5. 可选：`get_quant_technical --secid {secid}`（158+360+quant_verdict，注意 oos_status）
6. 可选：`get_stock_fund_flow --secid {secid} --limit 10`（量价背离）

## Alpha360 时序输入

```bash
python scripts/em.py get_alpha360_tensor --secid 0.002074
python scripts/em.py get_alpha360_score --secid 0.002074
python scripts/em.py get_alpha360_tensor --secid 0.002074 --include-tensor
```

- `tensor_rnn` (60,6)：LSTM / Transformer
- `tensor_conv` (6,60)：TCN
- 默认只返回 `sequence_summary`（通道形态、斜率），避免 JSON 过大

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
