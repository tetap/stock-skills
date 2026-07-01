---
name: stock-chip-analysis
description: >-
  A 股筹码集中度分析：获利比例、成本区间、90/70集中度。用于筹码、成本区、控盘、套牢盘、密集区突破。
---

# 筹码分析

## 何时转交 stock-main

| 用户意图 | 转交 |
|----------|------|
| 能不能买 / 全量分析 | **`/stock 分析 {标的}`** |
| 仅问成本区、集中度 | **本 Skill**（`/stock-chip`） |

## Workflow

1. `resolve_symbol --query "{标的}"`
2. `get_chip_distribution --secid {secid} --limit 60`
3. `get_realtime_quote --secid {secid}`（现价 vs 成本区）
4. `get_kline --secid {secid} --limit 60`（验证突破是否放量）

## 输出模板

```markdown
# {名称} 筹码分析

## 成本结构
- 平均成本
- 90% 成本区间 [{低}, {高}]
- 现价相对成本区位置

## 集中度
- 90 集中度趋势（收窄/发散）
- 获利比例

## 交易含义
- 支撑/压力来自哪一档密集区
- 突破密集区是否伴随放量

> 仅供参考，不构成投资建议。
```

## 解读 Checklist

- 90 集中度 < 10%：通常筹码较集中（需结合量价）
- 获利比例 > 80%：警惕获利回吐
- 突破成本区上沿需放量确认，否则可能是假突破
