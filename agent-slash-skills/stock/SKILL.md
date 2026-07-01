---
name: stock
description: >-
  A 股主命令：查价、投资分析、顾问视角一体化。/stock 或 $stock 后接自然语言。
  分析时按投资顾问流派拉取指标并给出统一报告，非分散小工具拼接。
disable-model-invocation: true
argument-hint: "[自然语言：查价 / 分析 / 顾问ID + 股票]"
---

# A 股主命令

用户在本条消息 **`/stock` 或 `$stock` 后面**的整段文字是自然语言请求。

## 示例

| 输入 | 行为 |
|------|------|
| `贵州茅台` | 查现价 |
| `帮我分析贵州茅台，给近期投资建议` | 综合顾问一体化分析 |
| `buffett 宁德时代` | 巴菲特视角分析 |
| `list` | 列出顾问流派 |

## 你要做的

1. **读取并遵循 stock-main skill**（主编排）
2. 意图路由见 stock-main：查价 / 顾问分析 / list
3. 分析路径：**按顾问指标拉数 → stock-investment-advisor 输出一份报告**，禁止按工具分节堆砌
4. MCP 或 `python scripts/em.py` 取数，禁止编造
5. 末尾：**仅供参考，不构成投资建议**

`$stock-analyze`、`$stock-role` 是快捷别名；用户已用 `$stock` 时不要 redirect。
