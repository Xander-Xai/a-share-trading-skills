# Shared Automation & Execution Governance v1.4

> 适用范围：本仓库长期养老与短中期两套策略从研究、模拟仓、人工实盘、半自动到自动执行的共同上位规则。
>
> 本文件不决定“买什么、买多少”。任何增加风险的订单先受 Level 0 `capital-eligibility-and-investor-risk-philosophy.md` 与 `pre-trade-order-authorization-contract.md` 硬门禁约束；通过后，资金比例、风险预算、单股/风险簇上限、建仓批次由 `capital-allocation-and-entry-policy.md` 管理；研究模型、Champion/Challenger、point-in-time 与模型晋级由 `research-model-governance.md` 管理；长期/短中期机器边界由 `strategy-boundary-contract.md` 管理；PIT 元数据由 `canonical-pit-data-contract.md` 管理。

## 1. 基本原则

自动化只能执行**已经被冻结、可复现、可审计并且符合当前治理版本的规则**，不能用自动化掩盖未经验证的策略。

统一阶段：

```text
Research only
→ Forward paper
→ Manual live
→ Automated research / manual order
→ Human-confirmed broker execution
→ Limited semi-auto
→ Full auto only after evidence + compliance + reliability gates
```

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

模型研究晋级与自动执行晋级是两道不同的 Gate：

```text
Good Model != Safe Auto Execution
Safe Executor != Positive Edge
Long Model != Short/Mid Model
```

## 2. Governance Bundle 必须完整记录

仓库存在多类上位治理/契约文件，不能只保存一个含义不明的 `policy_version`。

每个 Paper cohort、真实决策和订单至少保存：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_id
sleeve
strategy_version
model_version
```

2026-08-28 当前基线：

```text
capital_policy_version         = v2.5
automation_governance_version = v1.4
research_model_governance     = v3.2
strategy_boundary_contract    = v1
canonical_pit_data_contract   = v1
```

不同 artifact 的版本号独立演进；优先级由 `policy-precedence.md` 决定，不能按版本数字大小推断覆盖关系。

## 3. Paper 模式：执行本金与展示 NAV 分离

必须同时保存：

```text
paper_capital_rmb = 用于股数、100股单位、费用、滑点、仓位和风险
reporting_nav     = 100.00 起始的标准化绩效指数
```

禁止用 `NAV=100` 直接模拟 A 股股数。

模拟成交至少考虑：

- 100 股交易单位；
- 当期佣金、印花税等费用；
- 滑点与必要时的市场冲击；
- T+1 / 普通新买 A 股不能自由日内反向卖出；
- 涨跌停、停牌、跳空；
- 除权除息和公司行动；
- 大额订单执行拆单。

价格字段必须分开：

```text
baseline / decision price
planned order price
simulated fill
actual fill
```

## 4. 策略批次 ≠ 执行拆单

策略批次只从 Level 1A 读取：

```text
长期默认：40/30/30
长期例外：60/40 或 30/25/25/20

短中期默认：50/50
短中期三级确认例外：50/30/20
```

大额策略批次可拆成多个 child orders 管理流动性和滑点，但：

```text
执行拆单数量 != 策略批次数
```

自动化模块不得用多次报单伪造新的策略确认。

## 5. 跨策略同股 / 同因子必须聚合

长期和短中期可能同时研究甚至持有同一股票。券商通常只看到账户净持仓，因此运行时必须同时维护：

```text
Broker Net Position       = 券商真实账户持仓，执行层真相源
Strategy Virtual Position = 长期/短中期各自的逻辑子账
```

最低字段：

```text
strategy_id
sleeve = long | short_mid
stock_code
virtual_shares
broker_account_total_shares
```

账户级风险使用 Level 1A 定义：

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure

Account Cluster Exposure
= Long Cluster Exposure + Short/Mid-term Cluster Exposure
```

下单前检查：

- 同股账户级合计暴露；
- 同因子账户级合计暴露；
- 两策略是否对同股产生冲突订单；
- 卖出是否误卖另一策略虚拟份额；
- T+1 和 broker 可卖数量；
- `CAP_BREACH` 是否已存在；
- `strategy_id / sleeve` 是否与产生该决策的模型一致。

策略可以共享标的，不能共享第二套独立风险额度，也不能共享一个未声明边界的决策状态。

## 6. 模式晋级必须靠证据

### Paper → Manual Live

至少证明：

- point-in-time 数据链路稳定；
- 决策可复现；
- 无 look-ahead；
- 当前 Champion / 已批准模型状态明确；
- strategy context 与 sleeve-specific model 一致；
- Level 1A 风险政策未被绕过；
- 订单、成交、费用、分红/公司行动记账正确；
- 绩效与 Benchmark 口径正确；
- fail closed 可工作。

长期策略应继续跨财报/分红周期验证；短中期应积累足够 Forward 样本并覆盖不同 Regime。样本数不是自动晋级开关。

### Manual Live → Assisted / Semi-auto

必须证明：

- Paper 与真实成交可对账；
- 滑点/费用/impact 在模型容忍范围；
- Broker 净持仓与策略虚拟子账稳定 reconcile；
- 无重复下单、漏记成交、错误恢复；
- 人工 override 留痕。

### Full Auto

除策略 Edge 外还必须通过：

- broker/API 权限与账户约束；
- 程序化交易/自动报单当期合规；
- failure injection；
- restart/recovery；
- idempotency / duplicate-order protection；
- independent Kill Switch；
- 全量审计日志。

Full Auto 不是所有策略的强制终态。长期账户可以长期停留在 automated research / manual order 或 human-confirmed execution。

## 7. 下单前统一硬门禁

任何半自动/自动订单必须全部通过：

```text
current Level-0 capital eligibility loaded
current pre-trade authorization contract loaded
capital_eligibility = PASS for ENTRY/ADD
cash_need_gate = PASS for ENTRY/ADD
emergency_reserve_gate = PASS for ENTRY/ADD
debt_leverage_gate = PASS for ENTRY/ADD
available_idle_cash_rmb known and > 0 for ENTRY/ADD
personal/account sizing inputs complete
pretrade authorization_state = AUTHORIZED for ENTRY/ADD
current capital policy loaded
current automation governance loaded
current research model governance loaded
current strategy boundary contract loaded
current PIT data contract loaded
current skill version loaded
strategy_id / sleeve valid and matched to model
current model status valid (Champion or explicitly approved)
approved symbol / universe
fresh quote
fresh official-event check
point-in-time evidence valid
required data permitted-use status valid for production
position reconciled with broker truth
strategy virtual positions reconciled
no cross-strategy order conflict
no Policy Conflict
no required-data MISSING / CONFLICT
position/risk calculation valid
post-trade Final Short Cap valid when applicable
post-trade account symbol / cluster caps valid
strategy heat valid when applicable
broker connection healthy
compliance state valid
kill switch not active
```

若任一状态未知，默认不下新单。

## 8. CAP_BREACH 的执行语义

Level 1A 区分“计划下单超限”和“市场价格被动超限”。

新订单必须满足：

```text
Planned Post-Trade Exposure <= applicable Cap
```

若市场上涨导致已有持仓被动超限：

```text
state = CAP_BREACH
→ 禁止继续增加该方向风险
→ 生成再平衡/利润回流任务
→ 在现实可执行窗口恢复
```

除非 Hard Ceiling、流动性或其他紧急风险要求，不应为了机械比例在异常价格下无条件市价卖出。

## 9. Fail Closed / Kill Switch

以下任一情况默认停止**新订单**：

- 行情源异常/过期；
- 官方披露抓取失败；
- 代码/价格/复权冲突；
- point-in-time 状态不确定；
- `strategy_id / sleeve` 与模型不匹配；
- 数据 permitted-use / license 状态不允许目标生产用途；
- 治理版本或模型状态不一致；
- 本地与 Broker 持仓不一致；
- 虚拟子账与 Broker 净持仓无法对账；
- 长期/短中期同股订单冲突未解决；
- 仓位/风险计算异常；
- 重复订单检测触发；
- Broker 连接或订单提交结果未知；
- 连续下单失败；
- Hard Ceiling / circuit breaker；
- `Policy Conflict`；
- 人工紧急停止。

Fail closed 后只允许读取、对账、告警、取消允许取消的未成交订单，以及按既定风险计划管理已有仓位。不得猜测状态后继续买入。

若人工在 Level 0 未授权情况下仍增加风险，必须记录 `UNAUTHORIZED_MANUAL_RISK_INCREASE` 与 `rule_violation=true`；该交易不得被包装成策略合规执行。人工可以比系统更保守地少买或不买，但不能通过 override 放宽失败的资金资格、风险预算或仓位上限。

## 10. 订单幂等与 Broker 真相源

每个决策/订单必须有稳定 ID：

```text
strategy_id
decision_id
order_id
client_order_id / idempotency_key
```

规则：

- Broker acknowledgement / fill 是实际成交真相源；
- 本地状态更新前先持久化 Broker 返回；
- API 超时先查询订单状态，不盲目重试；
- 进程重启先 reconcile，再允许新单；
- 同一股票同一决策不能由两个 worker 重复提交；
- 跨策略同股订单先进行 conflict/netting 检查。

## 11. 最低审计字段

每个决策至少保存：

```text
as_of
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_id
sleeve
strategy_version
model_version
model_status
stock_code
thesis / reason
action
score / valuation / setup state
target_weight / risk budget
available_idle_cash_rmb
capital_eligibility
cash_need_gate
emergency_reserve_gate
debt_leverage_gate
pretrade_authorization_state
max_executable_shares
planned_entry_shares
binding_constraints
tranche
source_snapshot
data_snapshot_id
human_approved
```

每个订单至少保存：

```text
order_id
decision_id
strategy_id
sleeve
created/submitted/fill time
side
order_type
planned price/qty
actual price/qty
fees/taxes
slippage/impact
status
broker
```

原始决策不能被后来的结果覆盖；修订追加事件。

## 12. 默认保留人工确认的动作

即使未来允许 `AUTO_ORDER=true`，以下动作默认仍要求更高等级确认，除非另行完成风险评审：

- 新股票首次进入实盘；
- 单笔金额超过阈值；
- 全部清仓 / EXIT；
- 财报、监管或重大公司事件后的第一笔；
- Level-1 或 Skill / Champion 刚升级后的首次订单；
- Broker/runtime 异常恢复首单；
- 同股同时存在长期和短中期虚拟子账时的首次跨策略调仓。

## 13. 程序化交易 / 合规门禁

自动提交 A 股指令前，必须按**实际账户、实际券商、实际接口和当时最新规则**确认是否构成程序化交易，以及相应报告、测试、频率、接口和权限要求。

当前研究基线：

- 中国证监会《证券市场程序化交易管理规定（试行）》
  https://www.csrc.gov.cn/csrc/c101954/c7480579/content.shtml
- 上海证券交易所程序化交易管理实施细则
  https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml
- 深圳证券交易所程序化交易管理实施细则
  https://www.szse.cn/lawrules/rule/trade/t20250403_612770.html

这些链接只是研究基线。进入 Live/Semi-auto/Auto 前必须重新联网核验并向实际券商确认。

## 14. 安全与凭据

仓库不得提交：

- 券商密码；
- API key / secret；
- 交易账户号；
- 身份证件；
- 真实 token / cookie；
- 可重放交易授权的凭据。

凭据通过安全环境变量、密钥管理或券商官方授权机制注入。

## 15. 规则升级

运行系统不得自行修改 policy / Skill / Champion。

统一流程：

```text
发现问题
→ hypothesis
→ historical research
→ Challenger / shadow when applicable
→ forward test
→ 人工审核
→ version bump
→ repository consistency audit
→ paper shadow run
→ 再进入 live
```

任何 Level-1 规则变更、Champion Promotion 或执行治理变更，都必须触发全仓库一致性扫描。