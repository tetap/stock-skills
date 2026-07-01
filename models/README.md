# Alpha158 LightGBM / Alpha360 TCN 权重目录

| 文件 | 用途 | 生成方式 |
|------|------|----------|
| `alpha158_lgb.txt` | Alpha158 表格因子 LightGBM Booster | `python scripts/train_quant_models.py --lgb` |
| `alpha360_tcn.pt` | Alpha360 6×60 TCN 权重 | Qlib 训练后导出，或 `train_quant_models.py --tcn-init` |

未放置权重时，系统自动 **降级为启发式打分**（`get_quant_technical` 的 `model_status` 字段会标明）。

## 快速训练（本地 K 线，非 Qlib 官方流程）

```bash
pip install -r requirements-ml.txt
python scripts/train_quant_models.py --lgb --secids 0.002074,1.600519,0.300204
```

## 量化演示模型

仓库包含 **演示用** LightGBM 权重（小样本训练，**OOS 未通过**，仅供联调 `oos_status` / `quant_verdict.oos_warning`）：

| 文件 | 说明 |
|------|------|
| `alpha158_lgb.txt` | 演示 LGB 权重（勿用于实盘定调） |
| `alpha158_lgb.metrics.json` | OOS IC≤0 时 `get_quant_technical` 会提示评级上限 |

重新训练（需网络）：

```bash
bash scripts/train_demo_model.sh
```

缺失权重时从 GitHub 拉取或自动训练：

```bash
bash scripts/ensure_demo_models.sh
```

打 tag `v*` 推送时会通过 GitHub Actions 将权重附到 Release 资产。

正式研发见 `agent-skills/stock-quant-research/SKILL.md`（网格搜参 + OOS 验收）。

## 环境变量

- `ALPHA158_MODEL_PATH` → 自定义 LightGBM 模型路径
- `ALPHA360_MODEL_PATH` → 自定义 TCN 权重路径

## Qlib 官方模型

若使用 Microsoft Qlib 训练的 Alpha158/Alpha360 模型，将导出文件放到本目录并命名为上表文件名即可。
