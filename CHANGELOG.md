# Changelog

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。路线图见 [ROADMAP.md](ROADMAP.md)。

## [Unreleased]

### 新增

- **Walk-forward 回测**：`eastmoney/walk_forward.py` + `scripts/walk_forward_quant.py`（滚动 OOS fold）
- **`backtest_quant.py --method lgb`**：LGB 模型信号 long-only 回测
- **GluonTS 分位数输出**：P10/P50/P90 预测区间 + 不确定性（宽/中/窄）写入 `quant_verdict`
- **Alpha360 TCN 真实训练**：`--tcn` + OOS metrics（`alpha360_tcn.metrics.json`）
- **GluonTS DeepAR**：`eastmoney/gluonts_adapter.py`（PandasDataset 长表）+ `--deepar` 训练
- **`eastmoney/quant_training.py`**、**`eastmoney/tcn_model.py`** 统一训练/推理结构
- **GitHub Pages 文档站**：`scripts/build_pages.py` + `.github/workflows/pages.yml` → https://tetap.github.io/stock-skills/
- **`models/optional/`**：OOS 通过权重的 opt-in 目录说明
- Windows CI：`test.yml` 增加 `windows-latest` + `check.ps1`
- Live smoke：板块 `search_sectors`、C 流程 protocol、`xueqiu_hot`；`XUEQIU_TOKEN` 可选测 livenews

### 变更

- **`quant_verdict` 合成 DeepAR/TFT**：158/360/时序三维共振、分歧降置信、统一 `oos_warning`
- **`build_quant_verdict(ts_forecast=)`** 纳入时序模型分数与 OOS 状态
- **GluonTS TFT**：`--tft` 训练 TemporalFusionTransformer；推理优先 OOS 通过的 TFT
- **`train_demo_model.sh`**：4 股 + embargo 5d + 调优 LGB 默认流程
- `get_review_protocol(flow=C|D)` 返回 `required_tools` 清单
- 板块 `search_sectors` 单测回归（空 query、类型过滤、打分、跨类型）

## [0.1.1] - 2026-07-01

### 新增

- **`scripts/release_notes.sh`**：Release 正文从 CHANGELOG 自动提取
- **`scripts/validate_demo_metrics.py`**：演示 LGB metrics 路径与 OOS 门槛校验
- **`scripts/check.ps1`**：Windows 发布前检查（单测 + MCP parity）
- **`ROADMAP.md`**：v0.1.1 / v0.2.0 计划
- Live smoke：`get_kline`、`get_company_profile`

### 变更

- `release.yml` 使用 CHANGELOG 正文，不再 `generate_release_notes`
- `get_kline` 工具走 `get_kline_resilient`（东财失败时 AkShare 降级）
- `alpha158_lgb.metrics.json` 的 `model` 改为仓库相对路径
- `train_demo_model.sh` / `ensure_demo_models.sh` 训练或拉取后自动校验 metrics
- `evaluate_oos_metrics()` 统一 OOS 门槛（IC>0 且 direction_accuracy>50%）
- README / CONTRIBUTING 发布流程与测试计数对齐

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

[0.1.1]: https://github.com/tetap/stock-skills/releases/tag/v0.1.1
[0.1.0]: https://github.com/tetap/stock-skills/releases/tag/v0.1.0
