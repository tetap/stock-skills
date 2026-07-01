# 东方财富工具参考

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
```

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
