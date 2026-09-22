# Holding & Risk Management v3

> 本文件展开短中期持仓与风险规则。
>
> 最高资本/风险规则：`../../../shared/capital-allocation-and-entry-policy.md`。
> 涉及模型参数变更：`../../../shared/research-model-governance.md`。
> 涉及 Paper/Live/Broker：`../../../shared/automation-execution-governance.md`。

## 1. 三层风险必须同时通过

每笔交易不能只看“这只短线仓位多大”。必须同时满足：

```text
A. Strategy Risk
   per-trade risk / portfolio heat / factor heat

B. Strategy Capital Exposure
   单股、行业/因子、Final Short Cap

C. Account-level Aggregate Exposure
   长期 + 短中期同股/同因子合计
```

任一层失败，缩仓或跳过。

## 2. Final Short Cap

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
```

它是账户级短中期**新风险上限**，不是必须填满的目标。

新订单必须满足：

```text
Planned Post-Trade Short Exposure <= Final Short Cap
```

没有有效 setup：保持现金。

### 被动超限

价格上涨可能在无新订单时造成：

```text
Actual Short Exposure > Final Short Cap
```

此时：

```text
state = CAP_BREACH
→ 禁止增加短中期风险
→ 进入现实可执行的再平衡/利润回流
```

不是“规则失效”，也不能用漂移带继续加仓。

## 3. Operating Target 与 Hard Ceiling

### Operating Target

以当前短中期策略 NAV 为风险分母：

```text
单笔计划亏损：0.5%
全部未平仓初始风险：≤2%
单一行业/因子初始风险：≤1%
```

### Hard Ceiling

```text
单笔计划亏损：≤1%
全部未平仓初始风险：≤3%
```

0.5%/2% 是正常运行目标；1%/3% 是新计划风险硬上限。

真实跳空、跌停可能让实际亏损超过计划风险，因此 stop 不是保证成交价。尾部超损必须记录 risk event，不能反向把 Hard Ceiling 解释成最大实际亏损保证。

## 4. 仓位计算

先定义：

```text
E = planned entry
S = invalidation / stop
R = allowed currency loss
```

理论股数：

```text
shares = R / abs(E-S)
```

向下取可执行整手，再叠加：

```text
short single-symbol capital cap
short factor/industry capital cap
Final Short Cap
account-level symbol cap
account-level cluster cap
liquidity / security-specific minimum buy quantity and increment constraints
```

若止损太宽导致仓位太小，跳过，不放宽 stop 迁就仓位。

## 5. 跨策略同股 / 同因子聚合

如果长期仓已有同一股票：

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure
```

如果多个持仓共享同一经济因子：

```text
Account Cluster Exposure
= Long Cluster Exposure + Short/Mid-term Cluster Exposure
```

下单前必须检查 post-trade 合计值。

### Broker 执行

实际券商账户通常只看到净持仓，因此 Live 模式还要维护策略虚拟子账：

```text
strategy_id
sleeve
virtual_shares
broker_total_shares
```

短中期卖出不得误卖长期逻辑仍需持有的份额。

## 6. 策略批次

当前默认：

```text
50% Setup
50% Confirmation
```

三级确认例外：

```text
50% / 30% / 20%
```

后续批次只能因正向确认，不因亏损摊低成本。

### 允许的确认

- breakout holds；
- retest succeeds；
- relative strength improves；
- sector participation improves；
- catalyst / official fact strengthens；
- price progress confirms volume。

### 不允许

```text
第一笔亏损
→ 只因为成本更低就买第二批
```

执行拆单不是策略批次。

## 7. Holding State Machine

```text
strengthening
intact
weakening
invalidated
```

### strengthening

- thesis 更强；
- price/sector confirmation 改善；
- 风险预算、Final Short Cap、账户级同股/因子均允许。

可：HOLD 或按既定 confirmation tranche ADD。

### intact

原 thesis 成立但没有新确认。

通常 HOLD，不为了“仓位没满”补足。

### weakening

- relative strength 恶化；
- volume/price 失配；
- sector leadership 下降；
- event thesis 弱化；
- 时间窗口不工作。

考虑 TRIM / time stop。

### invalidated

失效条件成立。

按预先计划退出；不能把短线仓改名成长线仓。

## 8. 三维止损

```text
Price / Invalidation Stop
+ Thesis Stop
+ Time Stop
```

### 价格/失效

价格触发结构失效，按现实执行约束退出。

### Thesis

事件、基本面、行业或预期差被事实证伪时，即使价格尚未触发也可退出。

### Time Stop

默认计划5–15个交易日：

- 3–5日明显不工作且相对强度/成交量恶化：考虑减仓/退出；
- 到计划期仍无预期走势：重新承保；
- 超15日必须重新写 thesis/score/stop/risk。

这些天数是治理初值，不是最优定理。

## 9. Profit Management

一级优先级：

```text
R multiple
+ technical structure
+ original setup target
```

约 +1.5R～+2R 可考虑部分兑现1/3–1/2，剩余使用结构/trailing。

旧百分比区间只作观察：

```text
传统/周期 +3%～+5%
成长/科技 +6%～+10%
```

与 R/结构冲突时，R/结构优先。

+1.5R/+2R、3–5日等属于治理参数；调整必须通过 MFE/MAE、Forward 与 Challenger 流程。

## 10. MFE / MAE

每笔闭环至少记录：

```text
MFE_R
MAE_R
realized_R
holding_days
exit_reason
```

详细见：

`trade-ledger-mfe-mae-extension.md`

不能只根据最终 PnL 调整 stop/target。

## 11. 组合 Heat

Heat 是如果所有未平仓同时在各自初始失效点退出的计划风险近似，不等于投入金额。

日常：

```text
aggregate initial risk <=2%
industry/factor initial risk <=1%
```

Hard Ceiling：

```text
aggregate initial risk <=3%
```

如果 gap/event stress 明显高于名义 stop 风险，应缩小仓位或跳过。

## 12. 资本暴露

正常运营还检查：

- 单只短中期股票通常≤短中期策略 NAV约20%；
- 同一高度相关板块/因子通常≤短中期策略 NAV约40%；
- 同时持仓3–5只；
- 同行业/主导因子通常不超过2只。

这些都不能覆盖 shared 的更严格账户级 Cap。

## 13. 回撤熔断

从短中期策略权益高水位：

```text
-4% → 降低暴露，新单回到保守风险
-6% → 停止新开仓，只管理已有仓位并复盘
-8% → 暂停策略，正式复核后恢复
```

不通过重置高水位消除熔断。

## 14. 事件风险

二元事件前必须问：

- gap 5%–10% 反向时实际亏损多少？
- 跌停无法成交时风险多少？
- 明天是否财报、监管决定、重大股东减持、重组、诉讼？

名义 stop 无法控制事件 gap 时：减仓、隔离事件或不交易。

## 15. 大资金执行

策略批次不随资金机械增加。

大资金同一策略批次可以执行拆单，检查：

- ADV；
- bid/ask spread；
- order / ADV；
- impact；
- 限价；
- 部分成交；
- 涨跌停。

## 16. 持仓复核卡

```yaml
as_of:
capital_policy_version:
research_model_governance_version:
skill_version:
strategy_id:
code:
state: strengthening|intact|weakening|invalidated
current_R:
MFE_R:
MAE_R:
planned_invalidation:
time_stop_date:
current_short_exposure:
final_short_cap:
current_long_same_symbol_exposure:
account_symbol_exposure:
account_symbol_cap:
account_cluster_exposure:
account_cluster_cap:
portfolio_heat:
factor_heat:
cap_state: PASS|CAP_BREACH|BLOCKED
action: ADD|HOLD|TRIM|EXIT|NO_TRADE
reason:
```

## 17. 最终原则

```text
研究决定资格
风险决定仓位
执行决定能否成交
账户级合计风险高于策略标签
赢家/输家的近期结果不能自动改规则
```
