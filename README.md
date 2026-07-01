# Eastmoney Stock Skills

东方财富 A 股数据 + Agent Skills + **`/stock` 主命令**（查价 / **全量分析**），支持 Cursor、Claude Code、Codex CLI。

**核心亮点**：`/stock` 一个入口 — **个股全量分析**、**板块走势+选股**、**市场热点情绪**；拉齐基本面/技术/资金/筹码/**7×24 快讯**，输出简洁可操作建议，**不使用**投资顾问角色。

> **免责声明**：数据仅供参考，不构成任何投资建议。

---

## 5 分钟上手

### 0. 克隆并安装（Skills + Python 依赖 + MCP 一键完成）

```bash
git clone <your-repo-url> skills
cd skills

# 自动：.venv + pip install -r requirements.txt + 同步 .cursor/mcp.json + 安装 Skills
bash scripts/install.sh --target cursor --scope user
```

如需量化 ML 依赖（LightGBM / PyTorch）：

```bash
bash scripts/install.sh --target cursor --scope user --with-ml
```

仅链接 Skills、跳过 pip（已装过依赖时）：

```bash
bash scripts/install.sh --target cursor --scope user --skip-deps
```

手动验证 CLI：

```bash
.venv/bin/python scripts/em.py resolve_symbol --query "600519"
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
| 分析 Skills | `agent-skills/` | 主编排、全量分析 workflow |
| Cursor 快捷指令 | `agent-commands/` | `/stock` 主命令及专项快捷指令 |
| Claude/Codex 快捷指令 | `agent-slash-skills/` | `/stock` 或 `$stock` |

安装完成后**重启** Cursor / Claude Code / Codex。

**试试（安装后）：**

```
/stock 分析 贵州茅台
/stock 电池板块最近走势，给我几个看好的股票
/stock 今天有什么热点，情绪怎么样
```

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
| MCP 配置 | — | 运行 `install.sh` 生成本地 `.cursor/mcp.json`（见 `.cursor/mcp.json.example`） |

### 启用 MCP（推荐，模型可直接调全部数据工具）

1. 先运行 `bash scripts/install.sh --target cursor`（生成 `.cursor/mcp.json` 并安装依赖）
2. 打开 Cursor → **Settings → MCP**
3. 确认 `eastmoney-stock` 已加载（**36 个工具**）
4. 若未出现，重启 Cursor 或 Reload MCP

验证 MCP 进程：

```bash
source .venv/bin/activate
python -m mcp_server
```

### Cursor 使用示例

**主命令 `/stock`**：

```
/stock 贵州茅台
/stock 分析 宁德时代，近期能不能介入
/stock 帮我看看比亚迪，看几日线
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
/stock 分析 宁德时代，能不能买
/stock-analyze 比亚迪
/stock-fund 招商银行
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
$stock 贵州茅台
$stock 分析 宁德时代
$stock-analyze 比亚迪
$stock-fund 600519
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
| **主命令** | **`/stock`** | **`$stock`** | **`/stock 分析 贵州茅台`** |
| 全面分析（别名） | `/stock-analyze` | `$stock-analyze` | 同 `/stock 分析` |
| 资金面 | `/stock-fund` | `$stock-fund` | `/stock-fund 600519` |
| 筹码 | `/stock-chip` | `$stock-chip` | `/stock-chip 比亚迪` |
| K 线 | `/stock-kline` | `$stock-kline` | `/stock-kline 招商银行` |
| 基本面 | `/stock-basic` | `$stock-basic` | `/stock-basic 五粮液` |
| 板块 | `/stock-sector` | `$stock-sector` | `/stock-sector 半导体` |
| 事件 | `/stock-news` | `$stock-news` | `/stock-news 隆基绿能` |

---

## `/stock` 用法一览

| 场景 | 示例 | 模板 |
|------|------|------|
| 个股全量分析 | `/stock 分析 600519` | analysis-report.md |
| 板块 + 选股 | `/stock 电池板块走势，推荐几只` | sector-report.md |
| 热点 / 情绪 | `/stock 今天有什么热点` | market-brief.md |

### 个股分析

分析时 **尽量拉全 MCP/CLI 工具（≥20 次）**，再写 **6 节简洁报告**。

模板见 [`agent-skills/stock-main/analysis-report.md`](agent-skills/stock-main/analysis-report.md)。

### 分析会拉哪些数据

| 类别 | 工具 |
|------|------|
| **基本面** | 公司简介、**利润表/资产负债表/现金流**、估值、十大股东、股东户数 |
| **行情技术** | 现价、K 线、MA5/20/60、相对沪深300、指标解读、短线盯盘 |
| **资金筹码** | 个股/大盘资金流、筹码分布 |
| **事件舆情** | 大事提醒、个股新闻/公告、**7×24 快讯**、板块成分、龙虎榜 |

### 报告结构（6 节）

1. **结论与近期操作** — 看几日线、操作倾向、介入区间、确认/回避条件  
2. 基本面与估值  
3. 技术面  
4. 资金与筹码  
5. 事件与板块（含 **情绪热点**）  
6. 主要风险  

### 用法示例

```
/stock 分析 600519
/stock 帮我看看能不能买，看几日线
/stock 半导体板块最近怎么样，挑几只
/stock 今天市场情绪和热点
```

`/stock-analyze` 与 `/stock 分析` 相同。

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
├── eastmoney/             # Python 数据层（36 个 CLI/MCP 工具）
├── mcp_server/            # Cursor MCP：eastmoney-stock
├── scripts/
│   ├── em.py              # CLI
│   ├── install.sh         # 安装脚本
│   └── test.sh            # 测试
├── .cursor/
│   ├── mcp.json.example   # MCP 模板（install.sh 生成本地 mcp.json）
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
| **`stock-main`** | **`/stock` 主编排：全量拉数 + 6 节报告** |
| `stock-analysis-orchestrator` | 全量分析工具清单 |
| `stock-quick-lookup` | 快速查价 |
| `stock-fundamental-analysis` | 基本面 |
| `stock-technical-analysis` | 技术面 / K 线 |
| `stock-capital-flow` | 资金面 |
| `stock-chip-analysis` | 筹码 |
| `stock-historical-analysis` | 历史统计 |
| `stock-sector-analysis` | 板块 |
| `stock-event-research` | 新闻 / 公告 / 股东 |
| `eastmoney-api` | 工具规范、secid、限流 |

---

## 功能概览

| 能力 | 说明 |
|------|------|
| **`/stock` 全量分析** | 基本面三表 + 技术 + 资金 + 筹码 + 事件 |
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

## MCP 工具（36 个，Cursor）

含：7×24 快讯、雪球热门资讯（xueqiu_livenews）、板块模糊搜索、Alpha158/360 量化、审核协议等。完整列表：`python scripts/em.py list`

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
