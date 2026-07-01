---
name: stock-news
description: >-
  A 股事件/新闻/舆情。手动调用 /stock-news 或 $stock-news。含雪球热门资讯。
disable-model-invocation: true
argument-hint: "[股票名称或代码]"
---

# 事件 / 舆情

用户在本条消息 **`/stock-news` 或 `$stock-news` 后面**的文字是股票名称或代码（或市场热点词）。

## 你要做的

1. 读取并遵循 **stock-event-research** skill
2. `get_news_and_reports`（source=all）+ `get_market_news`（flash/xueqiu_livenews/xueqiu_hot）
3. 股东、龙虎榜、大事提醒按需拉取
4. 按时间梳理要点；雪球 `interrupt` 时引导登录 hq 页
5. 末尾免责声明
