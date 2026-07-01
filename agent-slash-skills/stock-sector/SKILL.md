---
name: stock-sector
description: >-
  A 股板块分析。手动调用 /stock-sector 或 $stock-sector。可接板块名，或留空看今日热点。
disable-model-invocation: true
argument-hint: "[板块名称，或 今日/热点]"
---

# 板块分析

用户在本条消息 **`/stock-sector` 或 `$stock-sector` 后面**的文字可能是板块名（如 `半导体`），或留空 / `今日` / `热点`。

## 你要做的

1. 读取并遵循 **stock-sector-analysis** skill
2. 指定板块 → `get_sector_detail`；未指定 → `get_sector_overview`
3. 末尾加免责声明
