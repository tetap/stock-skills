# 安全策略

## 报告漏洞

如发现 **凭据泄露、依赖漏洞、可被利用的代码路径** 等安全问题，请 **不要** 在公开 Issue 中粘贴 Cookie 或完整 `.cursor/mcp.json`。

推荐通过 GitHub **Private vulnerability reporting**（仓库 Security → Advisories → Report a vulnerability）。

若无法使用上述渠道，可发邮件至仓库维护者（请在 Issue 中 @ 维护者索取联系方式，勿公开 token）。

## 范围

| 在范围内 | 通常不在范围内 |
|----------|----------------|
| 本仓库 Python/MCP/脚本中的 RCE、路径穿越、凭据硬编码 | 东方财富等第三方接口变更或限流 |
| 依赖已知 CVE（`requirements.lock`） | 用户自行配置的绝对路径 `mcp.json` |
| install 脚本导致的不安全默认行为 | 模型输出「投资建议」内容本身（属产品合规范畴） |

## 支持的版本

| 版本 | 支持 |
|------|------|
| `master` 最新 | ✅ |
| 已发布 tag（如 `v0.1.x`） | ✅ 至下一 minor |
| 更旧 tag | ❌ |

## 安全使用提醒

- **勿** 将 `.cursor/mcp.json`、`.env` 提交到 Git
- MCP 子进程读取本机配置需 OS 磁盘权限，属预期行为而非漏洞
- 数据来自非官方公开接口，不适合承载交易密钥或实盘 API

## 响应预期

维护者将在 **7 个工作日内** 确认收到；修复时间取决于严重程度与复现难度。
