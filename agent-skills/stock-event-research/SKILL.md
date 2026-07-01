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
# 默认合并东财 7×24 + 新浪直播/滚动 + 雪球讨论热榜（top10）
python scripts/em.py get_market_news --news-type flash --limit 30 --source all
python scripts/em.py get_market_news --news-type flash --keyword 电池 --limit 15
python scripts/em.py get_market_news --news-type xueqiu_livenews --limit 15 --source xueqiu
python scripts/em.py get_market_news --news-type xueqiu_hot --limit 20 --source xueqiu
python scripts/em.py get_market_news --news-type sina_live --limit 20 --source sina
python scripts/em.py get_market_news --news-type headline --limit 15 --source eastmoney
```

## 个股新闻（必会）

```bash
# 东财搜索 API + 新浪筛选 + 雪球讨论热度（可选帖子需 XUEQIU_TOKEN）
python scripts/em.py get_news_and_reports --code 002074 --content-type news --limit 10 --source all --stock-name 国轩高科
python scripts/em.py get_news_and_reports --code 002074 --content-type news --source xueqiu
python scripts/em.py get_news_and_reports --code 002074 --content-type news --source eastmoney
python scripts/em.py get_news_and_reports --code 002074 --content-type announcement --limit 5
```

| 参数 | 含义 |
|------|------|
| `--source all` | 东财 + 新浪 + 雪球热度（默认） |
| `--source eastmoney` | 仅东财资讯搜索 / 7×24 |
| `--source sina` | 仅新浪 7×24 / 滚动（个股需 `--stock-name`） |
| `--source xueqiu` | 雪球 **热门资讯(livenews)** + 讨论热榜 + 帖子/研报（后两者需 Cookie） |

**热门资讯 API**：`https://xueqiu.com/statuses/livenews/list.json?category=6`（hq 页热门流，**需登录 Cookie**）

## 雪球登录与 pysnowball（研报/资金/帖子）

讨论**热榜**无需登录。帖子、研报、资金流向等需 Cookie：

1. 打开 **[https://xueqiu.com/hq](https://xueqiu.com/hq)** 并完成登录。
2. Cookie 复制 `xq_a_token` → `export XUEQIU_TOKEN='值'`（或整串 `XUEQIUTOKEN='xq_a_token=...;u=...;'`）。
3. 可选：`pip install browser-cookie3` 后自动从 Chrome/Safari 读取（须本机已登录）。
4. MCP：写入 `~/.cursor/mcp.json` → `eastmoney-stock.env.XUEQIU_TOKEN`，重启 Cursor。

**无 Cookie 时**：工具返回 `"interrupt": true`，Agent **必须中断**并提示用户先登录 hq 页，勿编造帖子内容。

```bash
python scripts/em.py get_xueqiu_auth_status
python scripts/em.py get_xueqiu_auth_guide
python scripts/em.py get_xueqiu_data --code 600519 --data-type report --limit 5
python scripts/em.py get_xueqiu_data --code 002074 --data-type capital_flow
python scripts/em.py get_market_news --news-type xueqiu_hot --limit 10 --source xueqiu
```

pysnowball 支持的 `data_type`：`report` `earningforecast` `capital_flow` `capital_history` `margin` `blocktrans` `quote` `pankou`

**Agent 流程**：

1. 先 `get_xueqiu_auth_status`；若 `authenticated: false` → 发登录引导并 **暂停**。
2. 用户配置后 → `get_news_and_reports --source xueqiu` 或 `get_xueqiu_data`。

分析个股或板块时，**务必**拉快讯并用 keyword 过滤相关行业词。

## 输出要点

- 按时间倒序列新闻要点
- 单独一节 **情绪/热点**：与标的或板块相关的 2~4 条快讯 + 短期影响（客观）
- 不做确定性预测

> 仅供参考，不构成投资建议。
