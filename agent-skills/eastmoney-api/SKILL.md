---
name: eastmoney-api
description: >-
  调用东方财富 A 股数据工具（行情、K线、财报、资金流、筹码、板块等）。
  当用户询问股票数据、东方财富接口、A股行情、财务或板块数据时使用。
---

# Eastmoney API

## CLI / 依赖

**推荐**：安装 Skills 时自动创建 `.venv` 并 `pip install`（无需手动装依赖）：

```bash
bash scripts/install.sh --target cursor --scope user
# 量化可选：bash scripts/install.sh --target cursor --with-ml
```

手动调试：

```bash
.venv/bin/python scripts/em.py list
.venv/bin/python scripts/em.py resolve_symbol --query "贵州茅台"
.venv/bin/python scripts/em.py get_realtime_quote --secid 1.600519
```

## MCP（推荐）

首次克隆后运行 `bash scripts/install.sh --target cursor`，会自动生成本地 `.cursor/mcp.json`（已 gitignore，勿提交绝对路径）。

模板见 `.cursor/mcp.json.example`。在 Cursor 设置中启用 MCP 后，模型可直接调用 `eastmoney-stock` 下的 **36 个工具**。

重启 Cursor 或刷新 MCP 后生效。MCP 命令：

```bash
source .venv/bin/activate
python -m mcp_server
```

## 命令路由（与 stock-main 配合）

完整说明见仓库根目录 [AGENTS.md](../../AGENTS.md)。

| 场景 | 入口 | 审核 |
|------|------|------|
| 个股全量 | `/stock 分析` + analysis-report | `get_review_protocol(flow=B)`，≥20 工具 |
| 板块选股 | sector-report / `/stock-sector` 含推荐 | flow=C |
| 市场热点 | `/stock-market` / market-brief | flow=D |
| 单维（资金/筹码/K线/基本面/舆情） | `/stock-fund` 等 | **无** review-protocol |

单维命令只拉相关工具；用户问「能不能买」→ 转 **`/stock 分析`**。

## Alpha360 / Alpha158 量化特征

| 数据集 | 结构 | 典型模型 |
|--------|------|----------|
| **Alpha360** | 6 通道 × 60 时间步 | TCN / LSTM / Transformer |
| **Alpha158** | 158 维表格因子 | LightGBM / Linear / TabNet |

```bash
# 量化综合（推荐：158+360+quant_verdict）
python scripts/em.py get_quant_technical --secid 0.002074

# Alpha158 表格因子
python scripts/em.py get_alpha158_factors --secid 0.002074
python scripts/em.py get_alpha158_score --secid 0.002074
python scripts/em.py get_alpha158_factors --secid 0.002074 --include-all-factors

# Alpha360 时序张量
python scripts/em.py get_alpha360_tensor --secid 0.002074
python scripts/em.py get_alpha360_score --secid 0.002074
```

分析时建议 **158 表格分 + 360 序列分** 交叉验证；`get_quant_technical` 返回 `model_status` 标明 LGB/TCN 是否已加载。

**模型权重**（可选，无权重时自动启发式）：
```bash
pip install -r requirements-ml.txt
python scripts/train_quant_models.py --lgb --limit 500 --grid
python scripts/backtest_quant.py --secid 0.300204 --grid-thresholds
python scripts/train_quant_models.py --tcn-init   # 仅占位结构，须 Qlib 重训
```
权重路径见 `models/README.md`；研发纪律见 `agent-skills/stock-quant-research/SKILL.md`。

## AkShare 降级

东方财富直连失败时，以下工具自动降级到 AkShare（需安装 `akshare`）：

`resolve_symbol`, `get_realtime_quote`, `get_kline`, `get_stock_fund_flow`, `get_fund_flow_rank`, `get_market_fund_flow`, `get_chip_distribution`, `get_sector_overview`, `get_sector_detail`

禁用降级：`export EASTMONEY_DISABLE_FALLBACK=1`

返回 dict 时可能含 `_data_source: akshare` 字段。

## Skills 目录结构

Skills **源码**在仓库根目录 `agent-skills/`（独立于 `.cursor`），各工具通过安装脚本链接或复制。

```
agent-skills/
├── eastmoney-api/
├── stock-quick-lookup/
└── ...
```

## 安装 Skills

```bash
# 安装到 Cursor + Claude + Codex + Agents 全局目录
bash scripts/install.sh --target all

# 仅 Cursor 全局
bash scripts/install.sh --target cursor

# 安装到当前仓库（团队共享）
bash scripts/install.sh --target cursor --scope project
bash scripts/install.sh --target claude --scope project

# 复制而非符号链接
bash scripts/install.sh --target all --copy

# 卸载
bash scripts/install.sh --target all --unlink
```

| 工具 | 全局路径 | 项目路径 |
|------|----------|----------|
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| Claude | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.codex/skills/` | `.codex/skills/` |
| Agents (Codex 标准) | `~/.agents/skills/` | `.agents/skills/` |

## 运行测试

```bash
bash scripts/test.sh
```

## secid 规则

- 上交所：`1.{6位代码}`（如 `1.600519`）
- 深交所/北交所：`0.{6位代码}`（如 `0.000001`）
- 不确定时先调 `resolve_symbol`

## 36 个工具

| 工具 | 主要参数 |
|------|----------|
| resolve_symbol | --query |
| search_stocks | --query, --limit |
| get_realtime_quote | --secid |
| get_kline | --secid, --period, --adjust, --limit |
| get_market_snapshot | --sort, --limit |
| get_company_profile | --secid, --code |
| get_financial_statements | --code, --report-type, --limit |
| get_valuation_metrics | --secid |
| get_shareholders | --code, --limit |
| get_shareholder_count | --code, --limit |
| get_major_events | --code, --limit |
| get_dragon_tiger | --code, --limit |
| get_news_and_reports | --code, --content-type, --limit, --source all\|xueqiu |
| get_market_news | --news-type flash/headline/xueqiu_livenews/xueqiu_hot/…, --source all\|xueqiu, --keyword, --limit |
| get_stock_fund_flow | --secid, --limit |
| get_fund_flow_rank | --limit |
| get_market_fund_flow | --limit |
| get_chip_distribution | --secid, --limit |
| get_historical_series | --secid, --limit, --indicators ma |
| compare_performance | --secid, --benchmark-code |
| search_sectors | --query, --sector-type, --limit |
| get_sector_overview | --sector-type, --sort, --limit |
| get_sector_detail | --board-name 或 --board-code, --detail-type members/kline/fund_flow |
| get_indicator_interpretation | --secid, --code |
| get_limit_up_gene | --secid, --code |
| get_short_term_monitor | --code |
| get_limit_up_history | --code, --limit |
| get_xueqiu_auth_guide | --reason |
| get_xueqiu_auth_status | （检测 Cookie / 浏览器） |
| get_xueqiu_data | --code, --data-type report/capital_flow/quote/…, --limit |
| get_alpha360_tensor | --secid, --seq-len, --include-tensor |
| get_alpha360_score | --secid |
| get_alpha158_factors | --secid, --include-all-factors |
| get_alpha158_score | --secid |
| get_quant_technical | --secid |
| get_review_protocol | --flow B\|C\|D |

## 限流与缓存

- 请求间隔 ≥ 0.6s，避免 IP 封禁
- 实时行情缓存 30s，K线/资金流 1h，财报/筹码 4~24h
- 接口失败时说明数据可能不可用，勿编造

## 合规

输出必须注明：**仅供参考，不构成投资建议。**

详细字段见 [reference.md](reference.md)
