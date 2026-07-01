# 安装

## 三端一次装齐（推荐）

```bash
bash scripts/install.sh --target all --scope user     # 全局
bash scripts/install.sh --target all --scope project  # 项目级
```

| 安装内容 | 作用 |
|---------|------|
| `agent-skills/` | 分析 workflow、报告模板 |
| `agent-commands/` | Cursor `/stock` 等命令 |
| `agent-slash-skills/` | Claude/Codex slash |
| `.venv/` | Python + MCP Server |
| `.cursor/mcp.json` | Cursor 36 工具 MCP |

## Cursor 专用

```bash
bash scripts/install.sh --target cursor --scope user
```

### 启用 MCP

1. 运行上述安装（生成 `.cursor/mcp.json`）
2. **Cursor → Settings → MCP** → 确认 `eastmoney-stock`（36 tools）
3. 未出现：**Reload MCP** 或重启 Cursor
4. 必须用 Cursor **打开本仓库**（MCP 路径写在项目内）

> 勿将 `.cursor/mcp.json` 提交到 Git（含本机绝对路径）。

## 可选参数

```bash
bash scripts/install.sh --with-ml      # LightGBM / PyTorch
bash scripts/install.sh --skip-deps    # 仅链接 Skills
bash scripts/install.sh --unlink       # 卸载
bash scripts/install.sh --help
```

## Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Target cursor -Scope user
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
```

## Claude Code / Codex

```bash
bash scripts/install.sh --target claude --scope user
bash scripts/install.sh --target codex --scope user
bash scripts/install.sh --target agents --scope user
```

| 工具 | 调用方式 |
|------|---------|
| Claude | `/stock 贵州茅台` |
| Codex | `$stock 贵州茅台` |

无 MCP 时 Skills 会引导调用 `scripts/em.py` 拉数。
