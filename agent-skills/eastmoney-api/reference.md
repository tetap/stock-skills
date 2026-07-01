# 东方财富工具参考

完整列表：`python scripts/em.py list`（**36 个**）

## 常用 CLI 示例

```bash
# 解析代码
python scripts/em.py resolve_symbol --query "茅台"

# 日K 前复权
python scripts/em.py get_kline --secid 1.600519 --period daily --adjust qfq --limit 120

# 利润表
python scripts/em.py get_financial_statements --code 600519 --report-type income --limit 8

# 个股资金流
python scripts/em.py get_stock_fund_flow --secid 1.600519 --limit 20

# 筹码分布
python scripts/em.py get_chip_distribution --secid 1.600519 --limit 60

# 行业板块
python scripts/em.py get_sector_overview --sector-type industry --limit 20
python scripts/em.py get_sector_detail --board-name "半导体" --detail-type members
python scripts/em.py get_sector_detail --board-name "半导体" --detail-type fund_flow

# 历史对比沪深300
python scripts/em.py compare_performance --secid 1.600519 --benchmark-code 000300

# 7×24 快讯 + 雪球热门资讯（浏览器 Cookie 自动读取）
python scripts/em.py get_market_news --news-type flash --source all --limit 20
python scripts/em.py get_market_news --news-type xueqiu_livenews --source xueqiu --limit 15
python scripts/em.py get_market_news --news-type xueqiu_hot --source xueqiu --limit 10

# 个股新闻（合并东财 + 新浪 + 雪球）
python scripts/em.py get_news_and_reports --code 600519 --content-type news --source all --limit 10

# 雪球鉴权诊断
python scripts/em.py get_xueqiu_auth_status
python scripts/em.py get_xueqiu_data --code 600519 --data-type report --limit 5

# 量化综合
python scripts/em.py get_quant_technical --secid 1.600519
python scripts/em.py get_alpha158_score --secid 0.002074

# 报告审核协议（B=个股 / C=板块 / D=市场简报）
python scripts/em.py get_review_protocol --flow B
```

## 雪球鉴权

- 热榜 `xueqiu_hot` 无需登录
- `xueqiu_livenews` / 帖子 / 研报：Chrome/Safari 登录 https://xueqiu.com/hq 后自动读 Cookie
- 返回 `status: auth_required` 或 `interrupt: true` 时，提示用户登录，勿编造数据
- MCP 子进程可能因 macOS 磁盘权限读不到 Cookie，CLI 正常而 MCP 失败时属权限差异

## K 线 period

`daily` | `weekly` | `monthly` | `1min` | `5min` | `15min` | `30min` | `60min`

## 复权 adjust

`none` 不复权 | `qfq` 前复权 | `hfq` 后复权

## 筹码字段

- profit_ratio：获利比例
- avg_cost：平均成本
- cost_90_low / cost_90_high：90% 成本区间
- concentration_90：90% 集中度（越低通常越集中）

## 资金流字段

- main_net_inflow：主力净流入
- super_large_net_inflow：超大单净流入
- large_net_inflow：大单净流入

## 审核协议 get_review_protocol

| flow | 场景 | min_tool_calls |
|------|------|----------------|
| B | 个股全量分析 | 20 |
| C | 板块 + 选股 | 12 |
| D | 市场热点简报 | 8 |

返回 JSON 含 `rounds`、`gates`、`mandatory_output`（§7 审核纪要）等字段。
