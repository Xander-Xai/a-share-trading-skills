# Causal Challenger Model v1.1

> 状态：`CHALLENGER / SHADOW ONLY`
>
> 本模型不得覆盖当前 `scoring-system.md` Champion，也不得直接改变真实下单。晋级规则见 `../../../shared/research-model-governance.md`。

## 1. 目的

把短中期研究从“所有信号混合打分”进一步拆成因果顺序：

```text
Eligibility
→ Business / Survival Quality
→ Expectation–Reaction Gate (ERG)
   ├─ Expectation Baseline
   ├─ Surprise
   ├─ Economic Materiality
   ├─ Prepricing
   └─ Post-event Reaction
→ Regime
→ Participation / Relative Strength
→ Research State
→ Price Structure / Execution
→ Risk
→ Position State
```

ERG 详细规则见 `expectation-reaction-gate.md`。它是 Challenger 的**子模块**，不是第五套平行端到端模型。

核心假设：短中期可交易机会更可能来自“预期变化 + 未充分定价 + 市场参与/反应 + 合适 Regime + 可执行价格结构”的组合，而不是单一技术指标、单一财报同比或单一所谓主力资金指标。

## 2. Hard Gates

任一项失败，Challenger research state 为 `REJECT`：

- ST/*ST、重大退市/会计/治理风险；
- 身份或代码无法确认；
- 数据不足或存在关键 point-in-time 冲突；
- 核心概念只有传闻、没有经济实质；
- 无法定义可接受的失效点；
- 涨跌停/跳空/停牌/流动性使风险预算不可执行；
- 新仓会突破 shared policy 的组合/因子/风险上限。

## 3. Challenger Score

> 以下权重是研究参数，不是生产规则，也不是“学术最优权重”。
>
> ERG 引入后采用 **State First, Rank Second**：Research State 先决定是否具备交易资格；Score 只用于相同/可比较 State 内部排序，不能让高分 `CANDIDATE` 自动越过低分 `CONFIRMED` 成为可执行交易。

```text
Business / Survival Quality     25
Valuation / Expectation Gap     15
Catalyst / Expectation Change   20
Market / Sector Regime          15
Participation / Relative Strength 15
Price Structure / Execution     10
Total                           100
```

### 3.1 Business / Survival Quality — 25

重点：

- 最新盈利与扣非趋势；
- 现金流/资产负债表；
- 会计质量；
- 行业位置；
- 治理与监管风险；
- 周期行业使用正常化盈利而非高点 PE。

### 3.2 Valuation / Expectation Gap — 15

不是寻找“股价跌得多”，而是判断当前价格是否仍存在合理的预期差：

- 相对自身历史估值；
- 相对同业；
- 盈利预期是否已经被充分反映；
- 催化兑现后是否仍有合理 upside；
- deep cyclical 不机械使用低 PE。

### 3.3 Catalyst / Expectation Change — 20

该维度必须调用 `expectation-reaction-gate.md`，不能只看“消息是否利好”。

优先可验证、能影响未来 5–60 个交易日预期的事件：

- 盈利/订单/产品价格变化；
- 产能投放；
- 已发布政策；
- 回购/分红/资本运作；
- 行业供需变化。

对事件至少检查：

```text
Expectation Baseline
→ Surprise
→ Economic Materiality
→ Prepricing
→ Post-event Reaction
```

要求：

- 没有可靠预期基线时，不能把高同比直接写成“超预期”；
- 订单必须检查订单额/收入、利润率、确认周期和履约风险；
- 商品/产品价格必须写明价格→成本→margin→profit 的传导路径；
- 政策必须落到需求、价格、成本、产能、竞争或利润；
- 正面信息若已经高度 Prepriced 或公告后出现负向相对反应，不得仅靠 headline 维持高催化判断；
- `source_tier`、`information_timestamp`、`first_tradable_timestamp` 必须保留。

降低：

- 纯传闻；
- 重复炒作旧消息；
- 已被价格完全交易的催化；
- 与公司实际收入利润关系很弱的概念。

### 3.4 Market / Sector Regime — 15

分类：

```text
TREND_FRIENDLY
ROTATIONAL_NEUTRAL
MEAN_REVERTING
RISK_OFF
```

检查：

- 宽基趋势与 breadth；
- 成交额与风险偏好；
- 行业相对强度；
- 龙头持续性；
- 突破成功/失败率；
- 高位股负反馈。

Regime 不适配时，不通过简单减几分强行交易；严重冲突可直接 `WAIT / NO_TRADE`。

### 3.5 Participation / Relative Strength — 15

三层证据：

```text
Participation
- 成交额
- 换手
- 流动性

Positioning
- 融资变化
- 龙虎榜机构席位
- 可验证持仓/大宗/回购等

Price Confirmation
- 相对宽基
- 相对行业
- 相对直接同业
```

对于事件驱动候选，优先使用 ERG 的**事件特定相对反应**，不要把 generic momentum 直接当成事件确认。

vendor “主力净流入”只能是补充证据，不得单独给满分。

### 3.6 Price Structure / Execution — 10

技术面主要负责执行：

- breakout / retest / reclaim；
- 关键支撑和失效点；
- ATR/波动；
- 距离阻力与止损；
- volume-price confirmation；
- realistic Reward/Risk；
- gap/limit risk。

不因为技术只有 10 分，就降低对执行风险的重视；严重 execution risk 仍是 Hard Veto。

## 4. 双状态机

ERG 后将“研究状态”与“持仓/执行生命周期”拆开，避免 `CONFIRMED = 必须买` 或 `READY = 研究已确认` 的混淆。

### 4.1 Research State

```text
REJECT
WATCH
CANDIDATE
CONFIRMED
INVALIDATED
```

规则见 `expectation-reaction-gate.md`。

### 4.2 Position State

```text
FLAT
READY
ENTRY
HOLD
ADD
TRIM
EXIT
COOLDOWN
```

允许：

```text
research_state = CONFIRMED
position_state = FLAT
```

例如逻辑已确认，但价格过度延伸、事件 gap 风险过高或 Reward/Risk 不合格。

### READY

建议最低要求：

```text
Hard Gates = PASS
research_state = CONFIRMED
Challenger Score >= research_threshold
Regime != RISK_OFF (unless strategy explicitly supports it)
Reward/Risk >= strategy_minimum
Risk Budget = PASS
```

`research_threshold` 是前测参数，不得静默替换 Champion 的 80/75/65 阈值；Score 不得覆盖 research state 或 Hard Gate。

## 5. 建仓、加仓与 Strategy-type Lock

仍受 shared policy：

```text
默认：50% Setup + 50% Confirmation
三级确认例外：50% / 30% / 20%
```

对本趋势/催化 Challenger：

```text
亏损本身不是第二批理由
```

第二批至少满足一个正向确认：

- breakout holds；
- retest succeeds；
- relative strength improves；
- sector/catalyst continues；
- 新事实强化 thesis。

每个交易 Thesis 在入场前声明：

```text
EVENT_MOMENTUM
TREND
MEAN_REVERSION
OTHER_EXPERIMENTAL
```

亏损中的 EVENT_MOMENTUM / TREND 不得静默改成 MEAN_REVERSION 或长期投资。变更 strategy type 必须结束/重新承保原 Thesis，并生成新记录。

注意：趋势/催化加仓规则不推广到长期价值分批建仓。

## 6. 退出

同时维护：

```text
Price / Invalidation Exit
Thesis Exit
Time Exit
Portfolio Risk Exit
```

+1.5R / +2R、3–5 日 time review 只作为当前治理初值；必须通过 MFE/MAE 和 Forward 数据校准。

## 7. Shadow Output Contract

每个候选至少同时输出：

```text
champion_score
champion_status
challenger_score
challenger_status
research_state
position_state
strategy_type
regime
catalyst_type
participation_state
relative_strength_state
entry_trigger
invalidation
expected_RR
risk_budget_status
key_disagreement
```

事件驱动候选还必须按 `expectation-reaction-gate.md` / `erg-output-schema.md` 保存 ERG 字段，至少包括：

```text
information_timestamp
first_tradable_timestamp
source_tier
expectation_baseline_type
expectation_confidence
surprise_direction
materiality_state
prepricing_state
reaction_state
```

缺失值必须显式 `null / UNRESOLVED`，不能凭空补齐。

`key_disagreement` 解释 Champion 与 Challenger 为什么不同。

## 8. Challenger 不得使用的后见之明

- 后来是否退市；
- 后来公布的财报；
- 后来发生的并购/政策；
- 后来最高价/最低价；
- 未来指数成分；
- 未来 ST 状态。

只允许使用 `as_of` 当时公开信息。

## 9. 验证与晋级

公平对照仍由 `champion-challenger-forward-test.md` 定义。

ERG 增量验证读取：

- `erg-forward-test-extension.md`；
- `statistical-promotion-guard.md`；
- `erg-validation-checklist.md`；
- `erg-promotion-criteria.md`。

必须做 ERG 模块消融，验证 Expectation/Surprise、Materiality、Prepricing、Reaction 分别是否增加样本外/Forward 的有效区分或改善风险，而不是把整套叙事一次性视为有效。

本模型只有在 shared Promotion Gate 通过后，才允许提出替换 Champion 或部分模块晋级的 PR/规则变更。
