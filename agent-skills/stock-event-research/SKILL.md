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
| `--source xueqiu` | 雪球讨论热榜 / 个股讨论热度 |

## 雪球 xq_a_token（帖子正文）

讨论**热榜/热度**无需登录。拉**个股帖子**需浏览器 Cookie 中的 `xq_a_token`：

1. 打开 [雪球](https://xueqiu.com) 并完成登录（未登录则先授权/注册）。
2. 开发者工具 → Application → Cookies → `xueqiu.com` → 复制 `xq_a_token`。
3. 配置环境变量：`export XUEQIU_TOKEN='粘贴值'`（MCP 用户写入 `~/.cursor/mcp.json` 的 `env.XUEQIU_TOKEN`）。
4. 重启 Cursor 或终端后重试。

**Agent 流程**：若返回含 `provider: xueqiu_auth_hint` 或帖子为空且需雪球正文：

1. 调用 `get_xueqiu_auth_guide`（或直接把上述步骤发给用户），并打开 https://xueqiu.com 引导登录。
2. **暂停**帖子相关步骤，等待用户回复「已配置雪球 token」。
3. 再执行 `get_news_and_reports --source xueqiu` 或 `--source all`。

```bash
python scripts/em.py get_xueqiu_auth_guide
python scripts/em.py get_xueqiu_auth_guide --reason auth_failed
```

分析个股或板块时，**务必**拉快讯并用 keyword 过滤相关行业词。

## 输出要点

- 按时间倒序列新闻要点
- 单独一节 **情绪/热点**：与标的或板块相关的 2~4 条快讯 + 短期影响（客观）
- 不做确定性预测

> 仅供参考，不构成投资建议。
