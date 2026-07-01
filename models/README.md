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

## 环境变量

- `ALPHA158_MODEL_PATH` → 自定义 LightGBM 模型路径
- `ALPHA360_MODEL_PATH` → 自定义 TCN 权重路径

## Qlib 官方模型

若使用 Microsoft Qlib 训练的 Alpha158/Alpha360 模型，将导出文件放到本目录并命名为上表文件名即可。
