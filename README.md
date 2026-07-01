# Eastmoney Stock Skills

东方财富 A 股数据 + Agent Skills + **`/stock` 主命令**（查价 / 顾问分析一体化），支持 Cursor、Claude Code、Codex CLI。

> **免责声明**：数据仅供参考，不构成任何投资建议。

---

## 5 分钟上手

### 0. 克隆并安装 Python 依赖

```bash
git clone <your-repo-url> skills
cd skills

python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

验证 CLI 是否可用：

```bash
python scripts/em.py resolve_symbol --query "600519"
# 应返回 secid: 1.600519
```

### 1. 一键安装到 Cursor + Claude Code + Codex（推荐）

```bash
# 全局：本机所有项目可用
bash scripts/install.sh --target all --scope user

# 项目级：仅当前仓库（可提交 Git，团队共享）
bash scripts/install.sh --target all --scope project
```

安装内容：

| 组件 | 目录 | 作用 |
|------|------|------|
| 分析 Skills | `agent-skills/` | 基本面/技术面/资金面等 workflow |
| Cursor 快捷指令 | `agent-commands/` | `/stock` 等 |
| Claude/Codex 快捷指令 | `agent-slash-skills/` | `/stock` 或 `$stock` |

安装完成后**重启** Cursor / Claude Code / Codex。

---

## Cursor 安装与使用

### 安装

```bash
cd skills
bash scripts/install.sh --target cursor --scope user    # 全局
bash scripts/install.sh --target cursor --scope project # 仅本仓库
```

安装路径：

| 类型 | 全局 | 项目 |
|------|------|------|
| 分析 Skills | `~/.cursor/skills/` | `.cursor/skills/` |
| 快捷指令 | `~/.cursor/commands/` | `.cursor/commands/` |
| MCP 配置 | — | `.cursor/mcp.json`（仓库已含） |

### 启用 MCP（推荐，模型可直接调 19 个数据工具）

1. 打开 Cursor → **Settings → MCP**
2. 确认 `eastmoney-stock` 已加载（读取本项目 `.cursor/mcp.json`）
3. 若未出现，重启 Cursor 或 Reload MCP

验证 MCP 进程：

```bash
source .venv/bin/activate
python -m mcp_server
```

### Cursor 使用示例

**主命令 `/stock`**（推荐：一条指令完成查价或顾问分析）：

```
/stock 贵州茅台
/stock 帮我分析一下贵州茅台，推断近期投资建议
/stock buffett 宁德时代
/stock list
```

专项快捷命令（仅当用户明确只要某一维度时使用）：

```
/stock-fund 600519
/stock-chip 比亚迪
/stock-kline 招商银行
```

不用快捷指令时，也可自然语言 + Skill：

```
用 stock-capital-flow 分析贵州茅台近20日主力流向
用 stock-analysis-orchestrator 全面分析五粮液
```

---

## Claude Code 安装与使用

### 安装

```bash
cd skills
bash scripts/install.sh --target claude --scope user
bash scripts/install.sh --target claude --scope project
```

安装路径：

| 类型 | 全局 | 项目 |
|------|------|------|
| 分析 Skills | `~/.claude/skills/` | `.claude/skills/` |
| 快捷指令（/stock） | 同上，目录名 `stock/` 等 | 同上 |

Claude Code 将 **Skills 目录名** 映射为 slash 命令，例如 `agent-slash-skills/stock/` → **`/stock`**。

仅安装快捷指令（不装分析 Skills）：

```bash
bash scripts/install.sh --target claude --what slash
```

仅安装分析 Skills：

```bash
bash scripts/install.sh --target claude --what skills
```

### Claude Code 使用示例

在 Claude Code 终端或对话中：

```
/stock 贵州茅台
/stock 600519
/stock-analyze 全面看看宁德时代值不值得研究
/stock-fund 招商银行
/stock-sector 今天什么板块涨得好
/stock-news 隆基绿能最近有什么公告
```

自然语言（会自动匹配分析 Skills）：

```
帮我用东方财富数据看一下比亚迪的筹码集中度
对比一下贵州茅台和沪深300近一年的表现
```

### Claude Code 数据从哪来？

Claude Code 本身不内置行情接口。需要在本仓库执行 CLI，或在本机配置 MCP（若 Claude 侧已接 MCP）：

```bash
source .venv/bin/activate
python scripts/em.py get_realtime_quote --secid 1.600519
python scripts/em.py get_chip_distribution --secid 1.600519
```

Skills 会引导 Claude 调用上述命令获取真实数据，**请勿让模型编造行情**。

---

## Codex CLI 安装与使用

### 安装

```bash
cd skills
bash scripts/install.sh --target codex --scope user
bash scripts/install.sh --target codex --scope project

# Codex 新标准路径（Agents）一并安装
bash scripts/install.sh --target agents --scope user
```

安装路径（两套路径 Codex 均可能扫描，脚本会同时链接）：

| 类型 | 全局 | 项目 |
|------|------|------|
| Codex Skills | `~/.codex/skills/` | `.codex/skills/` |
| Agents 标准 | `~/.agents/skills/` | `.agents/skills/` |

仅安装快捷指令：

```bash
bash scripts/install.sh --target codex --what slash
bash scripts/install.sh --target agents --what slash
```

安装后**重启 Codex CLI** 或新开 session。

### Codex 使用示例

Codex 用 **`$技能名`** 显式调用（推荐）：

```
$stock 贵州茅台现在多少钱
$stock-analyze 宁德时代
$stock-fund 600519
$stock-chip 比亚迪
$stock-sector 半导体
$stock-basic 五粮液
$stock-kline 招商银行
$stock-news 隆基绿能
```

也可输入 `/skills` 从列表中选择 `stock`、`stock-analyze` 等。

快捷 Skill 已设置 `allow_implicit_invocation: false`，**不会**被 Codex 自动误触发，需你手动 `$stock` 调用。

### Codex 拉取数据

在 Codex 工作目录打开本仓库，或确保 CLI 可执行：

```bash
cd /path/to/skills
source .venv/bin/activate
python scripts/em.py get_realtime_quote --secid 1.600519
```

---

## 快捷指令一览

| 作用 | Cursor / Claude | Codex | 示例 |
|------|-----------------|-------|------|
| **主命令（查价+顾问分析）** | **`/stock`** | **`$stock`** | **`/stock 分析 贵州茅台`** |
| 全面分析（别名） | `/stock-analyze` | `$stock-analyze` | 同 `/stock 分析 宁德时代` |
| 指定顾问（别名） | `/stock-role` | `$stock-role` | 同 `/stock lynch 300750` |
| 资金面 | `/stock-fund` | `$stock-fund` | `/stock-fund 600519` |
| 筹码 | `/stock-chip` | `$stock-chip` | `/stock-chip 比亚迪` |
| K 线 | `/stock-kline` | `$stock-kline` | `/stock-kline 招商银行` |
| 基本面 | `/stock-basic` | `$stock-basic` | `/stock-basic 五粮液` |
| 板块 | `/stock-sector` | `$stock-sector` | `/stock-sector 半导体` |
| 事件 | `/stock-news` | `$stock-news` | `/stock-news 隆基绿能` |

---

## `/stock` 主命令（一体化流程）

一条指令完成：**理解意图 → 选投资顾问 → 按顾问指标拉数 → 顾问统一解读**。

```
/stock 600519                              # 查现价
/stock 帮我分析贵州茅台，给近期投资建议      # 综合顾问报告（非工具拼接）
/stock buffett 宁德时代                     # 巴菲特视角
/stock list                                # 列出顾问流派
```

| 步骤 | 说明 |
|------|------|
| 1. 意图 | 查价 vs 分析 vs 指定顾问 |
| 2. 顾问 | 默认 `composite`；可指定 graham / buffett / lynch 等 |
| 3. 拉数 | **只拉该顾问关心的指标**（见 advisors.md） |
| 4. 输出 | **一份**顾问报告，禁止按「资金面/筹码/技术面」分工具堆砌 |

`/stock-analyze`、`/stock-role` 是快捷别名；子命令 `/stock-fund` 等仅在用户**明确**单一维度时使用。

### 顾问 Presets

| ID | 名称 | 代表人物 | 核心命题 |
|----|------|----------|----------|
| `graham` | 深度价值 | 格雷厄姆、施洛斯 | 安全边际、显著低于内在价值 |
| `buffett` | 质量价值 | 巴菲特、芒格 | 合理价格买入伟大公司 |
| `fisher` | 成长投资 | 菲利普·费雪 | 高成长优质企业长期持有 |
| `lynch` | GARP | 彼得·林奇 | PEG、成长与估值匹配 |
| `soros` | 宏观反身性 | 乔治·索罗斯 | 趋势、资金与叙事自我强化 |
| `dalio` | 宏观周期 | 瑞·达里奥 | 经济周期、相对强弱 |
| `composite` | 综合顾问 | 多流派 | 交叉验证，标注分歧 |

详细指标权重、行业 profile、报告模板见 [`agent-skills/stock-investment-advisor/advisors.md`](agent-skills/stock-investment-advisor/advisors.md)。

> **合规**：结论为「低估 / 合理 / 高估 / 观望 / 数据不足」，禁止「必涨 / 必买」。风格化研究，不构成投资建议。

---

## 安装脚本完整说明

```bash
bash scripts/install.sh --help
```

| 参数 | 说明 |
|------|------|
| `--target cursor` | 仅 Cursor |
| `--target claude` | 仅 Claude Code |
| `--target codex` | 仅 Codex（`~/.codex/skills`） |
| `--target agents` | Agents 标准路径（`~/.agents/skills`） |
| `--target all` | 以上全部 |
| `--scope user` | 安装到用户主目录（默认） |
| `--scope project` | 安装到当前仓库 |
| `--what skills` | 仅分析 Skills |
| `--what commands` | 仅 Cursor 命令 |
| `--what slash` | 仅 Claude/Codex 快捷 Skills |
| `--what all` | 全部（默认） |
| `--copy` | 复制文件（非符号链接） |
| `--unlink` | 卸载 |

**常用组合：**

```bash
# 三端一次装齐（最常用）
bash scripts/install.sh --target all --scope user

# 团队仓库：项目级 + 可 commit
bash scripts/install.sh --target all --scope project

# 卸载
bash scripts/install.sh --target all --unlink
```

---

## CLI 参考（不依赖 AI 工具）

```bash
source .venv/bin/activate

python scripts/em.py list
python scripts/em.py resolve_symbol --query "贵州茅台"
python scripts/em.py get_realtime_quote --secid 1.600519
python scripts/em.py get_kline --secid 1.600519 --limit 60
python scripts/em.py get_stock_fund_flow --secid 1.600519
python scripts/em.py get_chip_distribution --secid 1.600519
python scripts/em.py get_sector_detail --board-name "银行" --detail-type fund_flow
python scripts/em.py compare_performance --secid 1.600519 --benchmark-code 000300
```

---

## 项目结构

```
.
├── agent-skills/          # 分析 workflow（12 个 SKILL，含 stock-main 主编排）
├── agent-commands/        # Cursor 快捷指令（*.md）
├── agent-slash-skills/    # Claude/Codex 快捷指令（SKILL.md 目录）
├── eastmoney/             # Python 数据层（19 工具）
├── mcp_server/            # Cursor MCP：eastmoney-stock
├── scripts/
│   ├── em.py              # CLI
│   ├── install.sh         # 安装脚本
│   └── test.sh            # 测试
├── .cursor/
│   ├── mcp.json
│   ├── skills/            # 安装后生成
│   └── commands/          # 安装后生成
├── .claude/skills/        # 安装后生成（项目级）
├── .codex/skills/         # 安装后生成（项目级）
└── .agents/skills/        # 安装后生成（项目级）
```

---

## 分析 Skills 列表

| Skill | 用途 |
|-------|------|
| **`stock-main`** | **`/stock` 主编排：意图路由 + 顾问拉数 + 一体化输出** |
| `eastmoney-api` | 工具规范、secid、限流 |
| `stock-quick-lookup` | 快速查价 |
| `stock-fundamental-analysis` | 基本面 |
| `stock-technical-analysis` | 技术面 / K 线 |
| `stock-capital-flow` | 资金面 |
| `stock-chip-analysis` | 筹码 |
| `stock-historical-analysis` | 历史统计 |
| `stock-sector-analysis` | 板块 |
| `stock-event-research` | 新闻 / 公告 / 股东 |
| `stock-analysis-orchestrator` | 综合分析编排 |
| `stock-investment-advisor` | 投资顾问流派（配合 `/stock-role`） |

---

## 功能概览

| 能力 | 说明 |
|------|------|
| 实时行情 | 价格、涨跌幅、量额、PE、市值 |
| K 线 | 日/周/月/分钟，前复权/后复权 |
| 基本面 | 财报、估值、公司简介 |
| 资金面 | 主力净流入、排名、大盘资金 |
| 筹码 | 获利比例、成本区间、集中度 |
| 历史 | 涨跌幅、回撤、相对沪深300 |
| 板块 | 行业/概念、成分股、板块资金流 |
| 事件 | 新闻、公告、研报、龙虎榜 |

---

## secid 规则

| 市场 | 格式 | 示例 |
|------|------|------|
| 上交所 | `1.{代码}` | `1.600519` |
| 深交所 / 北交所 | `0.{代码}` | `0.000001` |

---

## MCP 工具（19 个，Cursor）

`resolve_symbol` · `search_stocks` · `get_realtime_quote` · `get_kline` · `get_market_snapshot` · `get_company_profile` · `get_financial_statements` · `get_valuation_metrics` · `get_shareholders` · `get_dragon_tiger` · `get_news_and_reports` · `get_stock_fund_flow` · `get_fund_flow_rank` · `get_market_fund_flow` · `get_chip_distribution` · `get_historical_series` · `compare_performance` · `get_sector_overview` · `get_sector_detail`

---

## AkShare 降级

东方财富直连失败时自动降级 AkShare：

```bash
export EASTMONEY_DISABLE_FALLBACK=1   # 禁用降级
```

---

## 测试

```bash
bash scripts/test.sh
```

---

## 注意事项

- 东方财富为非官方公开接口，内置限流（≥0.6s）与缓存
- 数据可能有延迟，结论需人工复核
- 请勿用于高频交易或商业分发

---

## License

MIT
