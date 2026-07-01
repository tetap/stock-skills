---
name: stock-event-research
description: >-
  A 股事件研究：公告、新闻、研报、十大股东、龙虎榜。用于最近有什么消息、股东变化、上榜原因、舆情。
---

# 事件研究

## Workflow

1. `resolve_symbol --query "{标的}"`
2. `get_news_and_reports --code {code} --content-type news --limit 10`
3. `get_news_and_reports --code {code} --content-type announcement --limit 5`
4. 可选：`--content-type report`
5. `get_shareholders --code {code}`
6. `get_dragon_tiger --code {code}`

## 输出模板

```markdown
# {名称} 事件梳理

## 近期新闻/公告
- 按时间倒序列要点

## 股东变化
- 主要股东及变动

## 龙虎榜（若有）
- 日期、买卖席位、原因

## 对股价的可能影响
- 客观描述，不做确定性预测

> 仅供参考，不构成投资建议。
```
