# CLI 示例

```bash
# 7×24 快讯（东财 + 新浪）
python scripts/em.py get_market_news --news-type flash --source all --limit 20
python scripts/em.py get_market_news --news-type flash --keyword 电池 --limit 15

# 个股新闻（合并东财 + 新浪）
python scripts/em.py get_news_and_reports --code 600519 --content-type news --source all --stock-name 贵州茅台 --limit 10
python scripts/em.py get_news_and_reports --code 600519 --content-type announcement --limit 5
```

## 数据源

| source | 说明 |
|--------|------|
| `all` | 东财 + 新浪（默认） |
| `eastmoney` | 东财 7×24 / 搜索 |
| `sina` | 新浪直播 / 滚动（个股需 `--stock-name`） |

## 合规

- 输出须注明：仅供参考，不构成投资建议
