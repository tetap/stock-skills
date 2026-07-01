# 贡献指南

感谢改进 [stock-skills](https://github.com/tetap/stock-skills)。提交 PR 前请阅读 [AGENTS.md](AGENTS.md)（命令路由与架构）。

---

## 环境

```bash
git clone git@github.com:tetap/stock-skills.git
cd stock-skills
bash scripts/install.sh --target cursor --scope user
```

Windows：`powershell -ExecutionPolicy Bypass -File scripts/install.ps1`

---

## 提交前检查

```bash
bash scripts/check.sh              # 单元测试 + MCP 工具 parity（必跑）
LIVE=1 bash scripts/smoke_live.sh  # 改接口层时建议跑
```

CI 会在 push/PR 时自动跑 `test.yml`（Python 3.12 + `requirements.lock`）。

PR 与 Issue 模板：`.github/pull_request_template.md`、`.github/ISSUE_TEMPLATE/`。

安全漏洞：见 [SECURITY.md](SECURITY.md)（勿在公开 Issue 粘贴 Cookie/Token）。

---

## 常见改动 checklist

### 新增/修改 MCP 工具

1. 实现 `eastmoney/` 逻辑
2. 注册 `eastmoney/tools.py` 的 `TOOL_NAMES` 与 `_run_primary`
3. 添加 `mcp_server/server.py` 的 `@mcp.tool()`
4. 更新 `agent-skills/eastmoney-api/SKILL.md` 工具表
5. 跑 `bash scripts/check.sh`（含 `test_mcp_parity`）

### 修改 Python 依赖

1. 改 `requirements.txt` 或 `requirements-ml.txt`
2. 运行 `bash scripts/lock_deps.sh`（ML 加 `--ml`）
3. 一并提交 `requirements.lock` / `requirements-ml.lock`

### 修改 Skills / 命令文档

- **源码目录**：`agent-skills/`、`agent-commands/`、`agent-slash-skills/`
- 安装脚本会链接到 `~/.cursor/skills` 等，**改源码后重新 install 或依赖 symlink 自动生效**
- 路由变更请同步 `AGENTS.md` 与 `stock-main/review-protocol.md`

### 量化模型

- 演示权重：`bash scripts/train_demo_model.sh` 或 `ensure_demo_models.sh`
- 勿将未通过 OOS 的模型当作「可定调策略」宣传；metrics 一并提交

---

## 不要提交

| 文件 | 原因 |
|------|------|
| `.cursor/mcp.json` | 含本机绝对路径，已 gitignore |
| `.venv/` | 本地环境 |
| 密钥 / Cookie / `XUEQIU_TOKEN` | 安全 |

模板：`.cursor/mcp.json.example`

---

## PR 说明建议

- **做了什么** + **为什么**
- 若只改文档，注明影响哪些命令/Skill
- 若改接口，附 `check.sh` 通过说明

---

## 发布

打 tag 会触发 `.github/workflows/release.yml`：从 [CHANGELOG.md](CHANGELOG.md) 提取对应版本说明，并附上 `models/alpha158_lgb.*`。

```bash
# 1. 更新 CHANGELOG（[Unreleased] → [x.y.z] - 日期）
bash scripts/check.sh

# 2. 打 tag 并推送
git tag v0.1.1 && git push origin v0.1.1
```

本地预览 Release 正文：

```bash
bash scripts/release_notes.sh v0.1.0
```

可选：安装 [GitHub CLI](https://cli.github.com/) 后手动创建/编辑 Release（CI 已自动创建时通常不必）：

```bash
brew install gh   # macOS；Windows: winget install GitHub.cli
gh auth login
gh release view v0.1.0
gh release edit v0.1.0 --notes-file /tmp/notes.md
```

见 [ROADMAP.md](ROADMAP.md) 了解下一版本计划。

---

## 行为准则

- 输出含免责声明：仅供参考，不构成投资建议
- 不引入投资顾问角色模块
- 保持 diff 聚焦，避免无关重构
