# CLI 参考

不依赖 AI，直接拉取东方财富数据。

```bash
source .venv/bin/activate

python scripts/em.py list
python scripts/em.py resolve_symbol --query "比亚迪"
python scripts/em.py get_realtime_quote --secid 0.002594
python scripts/em.py get_kline --secid 0.002594 --limit 60
python scripts/em.py get_stock_fund_flow --secid 0.002594
python scripts/em.py get_chip_distribution --secid 0.002594
python scripts/em.py get_sector_detail --board-name "电池" --detail-type fund_flow
python scripts/em.py get_quant_technical --secid 0.002594
python scripts/em.py get_review_protocol --flow B
```

## secid 规则

| 市场 | 格式 | 示例 |
|------|------|------|
| 上交所 | `1.{代码}` | `1.600519` |
| 深交所/北交所 | `0.{代码}` | `0.002594` |

## 测试

```bash
bash scripts/check.sh
LIVE=1 bash scripts/smoke_live.sh
```

## 相关文档

- [雪球授权](xueqiu.html)
- [GitHub 仓库](https://github.com/tetap/stock-skills)
- [Releases](https://github.com/tetap/stock-skills/releases)
