# Changelog

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。路线图见 [ROADMAP.md](ROADMAP.md)。

## [Unreleased]

### 计划

- Release 正文从 CHANGELOG 自动提取（见 `scripts/release_notes.sh`）
- 扩展 live smoke（K 线、公司概况）
- v0.1.1 文档与量化演示流程对齐

## [0.1.0] - 2026-07-01

### 新增

- **36 个 MCP/CLI 工具**：东方财富行情/财报/资金/筹码/板块/短线/雪球/量化/审核协议
- **`/stock` 主编排**：个股 B 流程（≥20 工具 + §7 审核纪要）、板块 C、热点 D
- **专项命令**：`/stock-fund`、`/stock-chip`、`/stock-kline`、`/stock-basic`、`/stock-sector`、`/stock-news`、`/stock-market`
- **`get_review_protocol(flow=B|C|D)`** 结构化审核门禁
- **Alpha158/360 + `get_quant_technical`**，含 `oos_status` / 演示 LGB 权重
- **雪球**：浏览器 Cookie 自动读取、`xueqiu_livenews`、热榜
- **AkShare 降级** + `get_kline_resilient`
- **安装**：`install.sh` / `install.ps1`（venv、lock 依赖、MCP 同步、Skills 链接）
- **测试/CI**：92 项单测、`check.sh`、live smoke workflow、MCP parity
- **文档**：`AGENTS.md`、`CONTRIBUTING.md`、Cursor rules、PR/Issue 模板

### 变更

- `.cursor/mcp.json` 改为本地生成（`mcp.json.example` + gitignore）
- 废弃 `stock-investment-advisor` / `stock-role` 顾问角色

### 说明

- 演示模型 **OOS 未通过**，`quant_verdict` 仅研究辅助
- 数据仅供参考，不构成投资建议

[0.1.0]: https://github.com/tetap/stock-skills/releases/tag/v0.1.0
