# 路线图

面向 [stock-skills](https://github.com/tetap/stock-skills) 的短期计划。详细变更见 [CHANGELOG.md](CHANGELOG.md)。

---

## v0.1.1 ✅（已发布）

Release 说明自动化、live smoke 扩展、OOS 门槛校验、`check.ps1`、K 线 resilient 工具路径。

---

## v0.2.0（进行中）

| 项 | 状态 |
|----|------|
| **Walk-forward / LGB 回测** | 🟢 `walk_forward_quant.py`、`backtest_quant.py --method lgb` |
| **GluonTS 分位数** | 🟢 P10/P50/P90 + uncertainty 写入 `quant_verdict` |
| **OOS 通过的可选模型** | 🟡 `models/optional/` + `ALPHA158_OPT_IN` 文档；Release artifact 待训出 |
| **板块/热点** | 🟢 C/D `required_tools`；`search_sectors` 回归单测 |
| **Windows CI** | 🟢 `test.yml` → `windows-latest` + `check.ps1` |

---

## v0.3.0（草案）

- OOS 模型 GitHub Release 资产 + `ensure_demo_models` opt-in 下载
- 板块 C 流程 E2E live 冒烟
- Windows `install.ps1` 纳入 CI

---

## 不在范围内

- 高频交易、实盘下单
- 投资顾问角色模块（已废弃）
- 保证第三方接口（东方财富等）长期稳定

---

## 如何参与

见 [CONTRIBUTING.md](CONTRIBUTING.md)。功能建议可用 Issue 模板 **Feature request**，标注期望版本（如 `0.2.0`）。
