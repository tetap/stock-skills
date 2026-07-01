# 量化策略研发路线（借鉴社区实践）

本仓库 **个股分析报告** 与 **可回测策略** 是两条线，勿混为一谈。

| 层级 | 本仓库现状 | 目标 |
|------|------------|------|
| L0 研究观点 | `/stock 分析` + review-protocol | 多轮审核的研究结论，**不是**回测收益承诺 |
| L1 因子/信号 | Alpha158/360 + quant_verdict | 须 OOS 检验 + 阈值网格 |
| L2 回测 | `scripts/backtest_quant.py` | IS 搜参 → OOS 验证 |
| L3 模拟盘 | 未实现 | Python 成交逻辑须与 L2 逐笔拟合 |
| L4 实盘 | 未实现 | API 切换前再跑一轮模拟 |

## 两条学习路线的映射

### 路线 1：复现他人 → 发现不可用

- **启示**：公开策略缺参数/隐藏逻辑 → 本仓库 `quant_verdict` 标注为「启发式」，报告 §7 须写「未过 OOS」时不得高置信。
- **动作**：复现 7 个策略后「全部放弃」是正常结果；应沉淀 **共性**（趋势+量能+风控）而非单个指标。

### 路线 2：整合 → 自研 → 拟合链

```
整理逻辑 → AI/人工迭代 → TV 回测 → Python 回测对齐 TV
→ 模拟盘对齐 Python → 实盘 API → 持续监控宏观/黑天鹅
```

本仓库已提供 **Python 回测第一步**；TradingView / 模拟盘 / 实盘需自行对接。

## 实验规范（与大模型训练同思路）

1. **数据**：约 2 年日线（`--limit 500`），前 **80% 时间** 样本内，后 **20%** 样本外。
2. **禁止**：在样本外上调参；禁止凭感觉设 `long_threshold` / `tanh scale`。
3. **网格**：`train_quant_models.py --grid`（LGB 超参）；`backtest_quant.py --grid-thresholds`（做多阈值）。
4. **验收**：OOS **IC > 0** 且 direction_accuracy > 50% 仅为最低门槛；还须 Sharpe、最大回撤、换手。
5. **报告**：若 OOS 未过，`quant_verdict` 在分析报告中只能作「辅助参考」，评级上限「右侧等待」。

## 命令

```bash
# 训练 LGB（80/20 + OOS 指标 JSON）
python scripts/train_quant_models.py --lgb --limit 500 --grid

# 单股 long-only 回测 + 阈值网格
python scripts/backtest_quant.py --secid 0.300204 --grid-thresholds

# 查看 OOS 是否通过
cat models/alpha158_lgb.metrics.json
```

## 与 `/stock` 分析的关系

- 分析流程见 [review-protocol.md](../stock-main/review-protocol.md)：**研究审核**，不是策略验收。
- 策略验收见本文：**回测 + OOS**，通过后再谈模拟盘。
- 永远假设：**市场下一秒可以黑天鹅**；程序能扛住之前，才考虑 unattended 运行。

## 诚实边界

- 当前 LGB 训练为 **轻量演示管线**，非 Qlib 工业流程。
- Alpha360 TCN 权重需自训；无权重时均为启发式。
- **真正赚钱的完整策略不会公开**；本仓库目标是帮你 **建立可验证的研发纪律**，而非提供圣杯。
