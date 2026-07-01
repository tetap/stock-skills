## 摘要

<!-- 做了什么、为什么（1~3 句） -->

## 变更类型

- [ ] 数据层 / MCP 工具（`eastmoney/`、`mcp_server/`）
- [ ] Skills / 命令文档（`agent-skills/`、`agent-commands/`、`agent-slash-skills/`）
- [ ] 量化 / 模型（`models/`、`scripts/train*.py`）
- [ ] CI / 安装脚本
- [ ] 其他

## Checklist

- [ ] 已读 [AGENTS.md](../AGENTS.md)（若改路由/报告流程）
- [ ] 已运行 `bash scripts/check.sh`
- [ ] 若新增 MCP 工具：`TOOL_NAMES` ↔ `server.py` 一致（`test_mcp_parity`）
- [ ] 若改依赖：已更新 `requirements.lock`（`bash scripts/lock_deps.sh`）
- [ ] 若改 Skills 路由：已同步 `AGENTS.md` / `review-protocol.md`
- [ ] 未提交 `.cursor/mcp.json`、`.venv/`、密钥

## 测试

<!-- check.sh 结果；若跑过 LIVE smoke 请注明 -->

```text

```

## 截图 / 示例（可选）

<!-- CLI 输出、报告片段等 -->
