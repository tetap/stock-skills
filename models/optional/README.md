# 可选 Alpha158 模型（opt-in）

v0.2.0 起预留 **通过 OOS 检验** 的 LightGBM 权重目录。默认仍使用仓库根目录的 **演示权重**（`../alpha158_lgb.txt`，OOS 未通过，带 `oos_warning`）。

## 启用方式

1. 将 OOS 通过的 `alpha158_lgb.txt` 与 `.metrics.json` 放入本目录
2. 设置环境变量：

```bash
export ALPHA158_OPT_IN=1
export ALPHA158_MODEL_PATH=models/optional/alpha158_lgb.txt
```

3. 校验：

```bash
python scripts/validate_demo_metrics.py --metrics models/optional/alpha158_lgb.metrics.json --strict-oos
```

`--strict-oos` 在 OOS 未通过时返回非零退出码；演示模型请勿加此参数。

## 获取权重

- 未来 GitHub Release 可能附带 `alpha158_lgb_oos.zip`（尚未发布）
- 本地训练：`python scripts/train_quant_models.py --lgb --grid --secids ...`（须自行验收 OOS）

## 行为说明

| 配置 | `get_quant_technical` |
|------|------------------------|
| 默认（无 opt-in） | 演示 LGB + `oos_passed=false` → 评级上限「右侧等待」 |
| opt-in + OOS 通过 | 使用 optional 权重，`oos_passed=true` 时可作更强辅助 |

**仍不构成投资建议**；正式策略须独立回测与模拟盘。
