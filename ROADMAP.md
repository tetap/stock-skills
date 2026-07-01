# 路线图

面向 [stock-skills](https://github.com/tetap/stock-skills) 的短期计划。详细变更见 [CHANGELOG.md](CHANGELOG.md)。

---

## v0.1.1 ✅（已发布）

Release 说明自动化、live smoke 扩展、OOS 门槛校验、`check.ps1`、K 线 resilient 工具路径。

---

## v0.2.0（下一 minor，草案）

| 项 | 说明 |
|----|------|
| **OOS 通过的可选模型** | 独立 artifact 或 opt-in 下载，默认仍用当前演示权重 + `oos_warning` |
| **板块/热点** | 强化 C/D 流程工具组合与 sector 模糊搜索回归 |
| **雪球** | 授权流程 E2E 文档；live smoke 在 token 可用时可选跑 xueqiu |
| **Windows CI** | `install.ps1` / `check.ps1` 纳入 GitHub Actions matrix |

---

## 不在范围内

- 高频交易、实盘下单
- 投资顾问角色模块（已废弃）
- 保证第三方接口（东方财富/雪球）长期稳定

---

## 如何参与

见 [CONTRIBUTING.md](CONTRIBUTING.md)。功能建议可用 Issue 模板 **Feature request**，标注期望版本（如 `0.2.0`）。
