# 路线图

面向 [stock-skills](https://github.com/tetap/stock-skills) 的短期计划。详细变更见 [CHANGELOG.md](CHANGELOG.md)。

---

## v0.1.1（下一 patch）

| 项 | 说明 |
|----|------|
| **Release 说明** | tag 推送时从 `CHANGELOG.md` 提取对应版本正文（`scripts/release_notes.sh`） |
| **Live smoke 扩展** | CI/本地冒烟覆盖 K 线 resilient、公司概况等高频路径 |
| **量化演示模型** | 文档化 OOS 门槛；`train_demo_model.sh` 输出与 metrics 校验更清晰 |
| **文档对齐** | README 测试计数、发布流程与 CONTRIBUTING 一致 |

---

## v0.2.0（下一 minor，草案）

| 项 | 说明 |
|----|------|
| **OOS 通过的可选模型** | 独立 artifact 或 opt-in 下载，默认仍用当前演示权重 + `oos_warning` |
| **板块/热点** | 强化 C/D 流程工具组合与 sector 模糊搜索回归 |
| **雪球** | 授权流程 E2E 文档；live smoke 在 token 可用时可选跑 xueqiu |
| **Windows** | `install.ps1` / `check.ps1` 与 CI matrix 对齐 |

---

## 不在范围内

- 高频交易、实盘下单
- 投资顾问角色模块（已废弃）
- 保证第三方接口（东方财富/雪球）长期稳定

---

## 如何参与

见 [CONTRIBUTING.md](CONTRIBUTING.md)。功能建议可用 Issue 模板 **Feature request**，标注期望版本（如 `0.1.1`）。
