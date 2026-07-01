# Alpha158 LightGBM / Alpha360 TCN / GluonTS DeepAR

| 文件/目录 | 用途 | 生成方式 |
|-----------|------|----------|
| `alpha158_lgb.txt` | Alpha158 LightGBM（调优 + embargo + 早停） | `python scripts/train_quant_models.py --lgb` |
| `alpha360_tcn.pt` | Alpha360 TCN 真实训练 | `python scripts/train_quant_models.py --tcn` |
| `gluonts_deepar/` | GluonTS DeepAR（PandasDataset 长表） | `python scripts/train_quant_models.py --deepar` |
| `gluonts_tft/` | GluonTS TemporalFusionTransformer | `python scripts/train_quant_models.py --tft` |

## 训练命令

```bash
pip install -r requirements-ml.txt

# Alpha158 LGB（默认调优超参 + 5 日 embargo 切分 + early stopping）
python scripts/train_quant_models.py --lgb --grid --secids 1.600519,0.002594,0.300204

# Alpha360 TCN（6×60 卷积，OOS metrics 写入 alpha360_tcn.metrics.json）
python scripts/train_quant_models.py --tcn --epochs 40

# GluonTS DeepAR（K 线 → 长表 item_id/timestamp/target，见 GluonTS 文档）
python scripts/train_quant_models.py --deepar --deepar-epochs 15

# GluonTS TFT（Temporal Fusion Transformer，优先用于推理）
python scripts/walk_forward_quant.py --secid 0.300204 --folds 5
```

## Walk-forward 回测

滚动 expanding window + 每 fold 样本内搜阈值 → 样本外验证：

```bash
python scripts/walk_forward_quant.py --secid 1.600519 --method auto --folds 5
```

GluonTS 数据格式参考：[Pandas DataFrame dataset](https://ts.gluon.ai/stable/tutorials/data_manipulation/pandasdataframes.html)

## Alpha158 LGB 调优要点

| 项 | 说明 |
|----|------|
| 正则 | `lambda_l1/l2`、`min_data_in_leaf`、`feature/bagging fraction` |
| 切分 | `temporal_split_with_embargo`（默认 5 日，与 forward label 对齐） |
| 早停 | `early_stopping_rounds=30` on OOS |
| 网格 | `--grid` 按 OOS IC 选优 |

## 量化演示模型

仓库包含 **演示用** LightGBM 权重（小样本训练，**OOS 未通过**，仅供联调 `oos_status` / `quant_verdict.oos_warning`）：

| 文件 | 说明 |
|------|------|
| `alpha158_lgb.txt` | 演示 LGB 权重（勿用于实盘定调） |
| `alpha158_lgb.metrics.json` | OOS 指标；`get_quant_technical` 读取 `oos_status` |

### OOS 最低门槛（演示 / 研发共用）

| 指标 | 门槛 | 说明 |
|------|------|------|
| 样本外 IC | **> 0** | 来自 `best.out_of_sample.ic` |
| 方向准确率 | **> 50%** | `direction_accuracy` |

未同时满足时 `oos_passed=false`，分析报告评级上限「右侧等待」。校验：

```bash
python scripts/validate_demo_metrics.py
```

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

可选 OOS 通过权重（opt-in）：见 [optional/README.md](optional/README.md)。

## 环境变量

- `ALPHA158_MODEL_PATH` → LightGBM
- `ALPHA360_MODEL_PATH` → TCN
- `GLUONTS_DEEPAR_PATH` → DeepAR 目录
- `GLUONTS_TFT_PATH` → TFT 目录

## Qlib 官方模型

若使用 Microsoft Qlib 训练的 Alpha158/Alpha360 模型，将导出文件放到本目录并命名为上表文件名即可。
