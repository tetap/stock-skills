---
name: stock-event-research
description: >-
  A 股事件与舆情：公告、新闻、研报、股东、龙虎榜、市场快讯热点。用于消息、情绪、热点、舆情。
---

# 事件与舆情研究

## 何时转交 stock-main

| 用户意图 | 转交 |
|----------|------|
| 个股能不能买 / 全量分析 | **`/stock 分析 {标的}`**（新闻是其中一环，非全部） |
| 仅梳理某股新闻/公告/股东 | **本 Skill**（`/stock-news`） |
| 全市场热点/情绪 | **`/stock-market`**（D 流程） |

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
# 东财搜索 API + 新浪筛选 + 雪球讨论热度/热门资讯（浏览器 Cookie 自动读取）
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

## 雪球 Cookie（自动读取，无需手动配 env）

讨论**热榜**无需登录。热门资讯 / 帖子 / 研报会 **自动从本机 Chrome/Safari 读取 Cookie**：

1. 在 Chrome 或 Safari 打开 **[https://xueqiu.com/hq](https://xueqiu.com/hq)** 并登录。
2. **直接调用工具**，无需 `export XUEQIU_TOKEN`。
3. 读取失败时：重新执行 `bash scripts/install.sh --target cursor`（自动 pip）；macOS 给 Cursor **完全磁盘访问权限**。
4. `XUEQIU_TOKEN` 仅作 CI / 无浏览器环境兜底。

```bash
python scripts/em.py get_xueqiu_auth_status
python scripts/em.py get_market_news --news-type xueqiu_livenews --source xueqiu --limit 15
python scripts/em.py get_xueqiu_data --code 600519 --data-type report
```

**Agent 流程**：先 `get_xueqiu_auth_status`；若 `authenticated: false` → 提示用户登录 hq 页，**不要**要求手动复制 token（除非自动读取持续失败）。

分析个股或板块时，**务必**拉快讯并用 keyword 过滤相关行业词。

## 输出要点

- 按时间倒序列新闻要点
- 单独一节 **情绪/热点**：与标的或板块相关的 2~4 条快讯 + 短期影响（客观）
- 不做确定性预测

> 仅供参考，不构成投资建议。
