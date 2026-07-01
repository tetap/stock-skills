---
name: stock-event-research
description: >-
  A 股事件与舆情：公告、新闻、研报、股东、龙虎榜、市场快讯热点。用于消息、情绪、热点、舆情。
---

# 事件与舆情研究

## 个股事件

1. `resolve_symbol --query "{标的}"`
2. `get_news_and_reports --code {code} --content-type news --limit 10`
3. `get_news_and_reports --code {code} --content-type announcement --limit 5`
4. 可选：`--content-type report`
5. `get_major_events --code {code}`
6. `get_shareholders` / `get_dragon_tiger`

## 市场热点与情绪（必会）

```bash
# 默认合并东财 7×24 + 新浪直播/滚动
python scripts/em.py get_market_news --news-type flash --limit 30 --source all
python scripts/em.py get_market_news --news-type flash --keyword 电池 --limit 15
python scripts/em.py get_market_news --news-type sina_live --limit 20 --source sina
python scripts/em.py get_market_news --news-type headline --limit 15 --source eastmoney
```

## 个股新闻（必会）

```bash
# 东财搜索 API（替代已下线的 datacenter 新闻报表）+ 可选新浪补充
python scripts/em.py get_news_and_reports --code 002074 --content-type news --limit 10 --source all --stock-name 国轩高科
python scripts/em.py get_news_and_reports --code 002074 --content-type news --source eastmoney
python scripts/em.py get_news_and_reports --code 002074 --content-type announcement --limit 5
```

| 参数 | 含义 |
|------|------|
| `--source all` | 东财 + 新浪（默认） |
| `--source eastmoney` | 仅东财资讯搜索 / 7×24 |
| `--source sina` | 仅新浪 7×24 / 滚动（个股需 `--stock-name`） |

分析个股或板块时，**务必**拉快讯并用 keyword 过滤相关行业词。

## 输出要点

- 按时间倒序列新闻要点
- 单独一节 **情绪/热点**：与标的或板块相关的 2~4 条快讯 + 短期影响（客观）
- 不做确定性预测

> 仅供参考，不构成投资建议。
