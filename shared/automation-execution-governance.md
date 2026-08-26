# Shared Automation & Execution Governance v1.1

> 适用范围：本仓库长期养老与短中期两套策略从研究、模拟仓、人工实盘、半自动到自动执行的共同上位规则。
>
> 本文件不决定“买什么、买多少”。资金比例、风险预算、单股/风险簇上限、建仓批次仍以 `capital-allocation-and-entry-policy.md` 为唯一 Source of Truth。

## 1. 基本原则

自动化只能自动执行**已经被冻结、可复现、可审计的规则**，不能用来掩盖未经验证的策略。

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

默认状态：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

没有完成验证和合规门禁时，不得因为券商接口“技术上可以下单”就启用无人值守交易。

## 2. Policy / Skill 版本必须分开记录

仓库有两个 Level-1 规则文件，不能只保存一个含义不明的 `policy_version`。

最低要求：

```text
capital_policy_version
automation_governance_version
skill_version
strategy_version
```

当前设计基线例如：

```text
capital_policy_version      = v2.3
automation_governance_version = v1.1
```

不同文件的版本号是各自 artifact 的版本，不能因为数字大小不同就推断谁“更新”。优先级由 `policy-precedence.md` 决定。

## 3. Paper 模式必须区分“执行本金”和“展示 NAV”

模拟系统必须同时保存：

```text
paper_capital_rmb   = 模拟执行本金，用于股数、100股单位、费用、滑点和仓位计算
reporting_nav       = 100.00 起始的标准化绩效指数，用于跨本金比较
```

禁止只使用 `NAV=100` 就直接模拟股数和 A 股最小交易单位。

模拟成交至少考虑：

- 100 股交易单位；
- 佣金、印花税等当期适用费用；
- 滑点；
- T+1 / 当日不可自由反向卖出约束；
- 涨跌停、停牌、跳空；
- 除权除息；
- 大额订单的执行拆单。

必须区分：

```text
baseline / decision price
planned order price
simulated or actual fill price
```

## 4. 策略批次与执行拆单

策略批次只能来自 shared capital policy：

- 长期默认 40/30/30，按 policy 允许 2 批或 4 批例外；
- 短中期默认 50/50，按 policy 允许 50/30/20 三级确认例外。

大额订单可以拆成多个子订单，但：

```text
执行拆单数量 ≠ 策略批次数
```

任何 automation/runtime 模块都不得通过“多下几笔订单”绕过策略批次规则。

## 5. 跨策略同股 / 同因子必须聚合

长期和短中期可能同时研究甚至持有同一股票。券商端通常只看到**账户净持仓**，因此必须同时维护：

```text
Broker Net Position      = 券商真实账户持仓，执行层真相源
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

下单前必须检查：

- 同一股票长期 + 短中期的账户级合计暴露；
- 同一风险簇长期 + 短中期的账户级合计暴露；
- 是否存在两个策略对同一股票发出互相冲突的订单；
- 本次卖出是否会误卖另一策略逻辑上仍需持有的份额；
- T+1、可卖数量与券商实际持仓是否一致。

默认原则：

```text
策略可以共享研究标的
但不能共享“独立风险额度”
```

同股/同因子上限最终按账户级合计暴露执行。

## 6. 模式晋级必须靠证据

### Paper → Manual Live

至少证明：

- point-in-time 数据链路稳定；
- 决策可复现；
- 没有未来数据泄漏；
- 风险政策没有被绕过；
- 订单、成交、费用、分红/公司行动可正确记账；
- 绩效可解释；
- 出错时系统会 fail closed。

短中期可使用较多交易样本判断 edge；长期策略应至少经历数月工程前测，并保留完整财报/分红周期继续验证策略本身。

### Manual Live → Assisted / Semi-auto

必须证明：

- 模拟与真实成交可对账；
- 滑点和费用在模型容忍范围；
- broker position 与本地 ledger 可稳定 reconcile；
- 没有重复下单、漏记成交、错误恢复；
- 人工 override 有记录。

### Full Auto

除策略 edge 外，还必须通过：

- broker/API 权限与账户约束确认；
- 程序化交易/自动报单相关合规检查；
- failure injection；
- restart/recovery；
- idempotency / duplicate-order protection；
- independent kill switch；
- 全量审计日志。

## 7. 下单前统一硬门禁

无论长期还是短中期，自动/半自动下单前必须全部通过：

```text
current capital policy loaded
current automation governance loaded
current skill version loaded
approved symbol / universe
fresh quote
fresh official-event check
position reconciled with broker truth
strategy virtual positions reconciled
no cross-strategy order conflict
no Policy Conflict
no data MISSING / CONFLICT on required fields
position/risk calculation valid
post-trade single-stock / cluster / heat limits valid
broker connection healthy
compliance state valid
kill switch not active
```

策略可以更保守，不能更宽松。

## 8. Fail Closed 与 Kill Switch

出现以下任一情况，默认停止**新订单**：

- 行情源异常或过期；
- 官方披露抓取失败；
- 代码/价格/复权冲突；
- 本地持仓与券商持仓不一致；
- 策略虚拟子账与券商净持仓无法对账；
- 长期/短中期对同一股票出现未解决的订单冲突；
- 仓位或风险计算异常；
- 重复订单检测触发；
- 券商连接状态未知；
- 订单提交结果不确定；
- 连续下单失败；
- 规则版本不一致；
- Hard Ceiling / circuit breaker 触发；
- `Policy Conflict`；
- 人工紧急停止。

Fail closed 后只允许执行预定义安全动作，例如读取、对账、告警、取消允许取消的未成交订单、按既定风险计划管理已有仓位。不得“猜测状态后继续买入”。

## 9. 订单幂等与券商真相源

每个 decision/order 必须有稳定 ID：

```text
strategy_id
decision_id
order_id
client_order_id / idempotency_key
```

规则：

- broker acknowledgement / fill 是实际成交真相源；
- 本地状态更新前先持久化 broker 返回；
- API 超时后先查询订单状态，不盲目重试；
- 进程重启后先 reconcile，再允许新订单；
- 同一股票同一决策不得被两个 worker 重复提交；
- 跨策略对同一股票的订单必须经过 conflict/netting 检查。

## 10. 最低审计字段

每个决策至少保存：

```text
as_of
capital_policy_version
automation_governance_version
skill_version
strategy_version
strategy_id
sleeve
stock_code
thesis / reason
action
score / valuation or setup state
target_weight / risk budget
tranche
source snapshot
human_approved
```

每个订单至少保存：

```text
order_id
decision_id
strategy_id
created/submitted/fill time
side
order type
planned price/qty
actual price/qty
fees/taxes
slippage
status
broker
```

原始决策字段不可用后来的结果覆盖；修订必须追加新事件。

## 11. 人工确认默认保留的动作

即使未来允许 `AUTO_ORDER=true`，以下动作默认仍应要求更高等级确认，除非单独完成风险评审：

- 新股票首次进入实盘组合；
- 单笔金额超过预设阈值；
- 全部清仓 / EXIT；
- 财报、监管、重大公司事件后的第一笔交易；
- shared policy 或 Skill 刚升级后的首次订单；
- broker/runtime 发生异常后的恢复首单；
- 同一股票同时存在于长期和短中期子账时的首次跨策略调仓。

## 12. 程序化交易 / 合规门禁

自动提交 A 股交易指令前，必须按**实际账户、实际券商、实际接口和当时最新规则**确认是否构成程序化交易以及相应报告、测试、频率、接口和权限要求。

当前研究基线包括：

- 中国证监会《证券市场程序化交易管理规定（试行）》
  https://www.csrc.gov.cn/csrc/c101954/c7480579/content.shtml
- 上海证券交易所程序化交易管理实施细则
  https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml
- 深圳证券交易所程序化交易管理实施细则
  https://www.szse.cn/lawrules/rule/trade/t20250403_612770.html

这些链接是研究基线，不代表未来仍未变化。进入 Live/Semi-auto/Auto 前必须重新联网核验并向实际券商确认。

## 13. 安全与凭据

仓库不得提交：

- 券商密码；
- API key / secret；
- 交易账户号；
- 身份证件；
- 真实 token / cookie；
- 可用于重放交易授权的凭据。

凭据必须通过安全的环境变量、密钥管理或券商官方授权机制注入。

## 14. 规则升级

运行中的系统不得自行修改 policy 或 Skill。

统一流程：

```text
发现问题
→ hypothesis
→ 历史分析 / forward test
→ 新旧版本并行比较
→ 人工审核
→ version bump
→ repository consistency audit
→ paper shadow run
→ 再进入 live
```

任何 Level-1 资金规则或本自动化治理规则变更，都必须触发全仓库一致性扫描。
