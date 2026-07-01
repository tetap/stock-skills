# stock-skills

**东方财富 A 股数据 × Agent Skills × `/stock` 一键分析**

在 **Cursor / Claude Code / Codex** 里用自然语言查行情、做全量个股分析、扫板块选股、看市场热点。  
33 个 MCP 工具拉齐 **基本面 · 技术 · 资金 · 筹码 · 舆情 · 量化**，输出带 **§7 审核纪要** 的结构化报告。

> **免责声明**：数据来源于公开接口，仅供参考，**不构成任何投资建议**。

## 核心亮点

| 能力 | 说明 |
|------|------|
| **一个入口 `/stock`** | 查价、个股全量分析、板块+选股、市场热点，Agent 自动路由 |
| **真数据，不编造** | 33 个 MCP/CLI 工具；东财失败自动 AkShare 降级 |
| **全量个股分析** | 三表财报 + 技术 + 资金筹码 + 7×24 快讯 + Alpha158 量化辅助 |
| **审核门禁** | review-protocol B/C/D，终稿含 **§7 审核纪要** |
| **三端即用** | Cursor MCP + Claude `/stock` + Codex `$stock` |
| **CLI 独立可用** | `python scripts/em.py …` 不依赖 AI |

## 快速开始

```bash
git clone https://github.com/tetap/stock-skills.git
cd stock-skills
bash scripts/install.sh --target cursor --scope user
```

1. **重启 Cursor**
2. 用 Cursor **打开本仓库目录**
3. 对话输入：

```
/stock 600519
/stock 分析 宁德时代，看几日线能不能介入
/stock 电池板块最近走势，推荐几只
```

验证：

```bash
.venv/bin/python scripts/em.py resolve_symbol --query "贵州茅台"
.venv/bin/python scripts/em.py list
```

[→ 详细安装说明](install.html) · [→ 用法与命令](usage.html)
