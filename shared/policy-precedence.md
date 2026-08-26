# Repository Policy Precedence

> 本文件定义全仓库规则层级。资金/风险以 `capital-allocation-and-entry-policy.md` 为 Source of Truth；模拟仓、Broker 与自动化安全以 `automation-execution-governance.md` 为上位规则；研究证据、Champion/Challenger、point-in-time、Benchmark 与模型晋级以 `research-model-governance.md` 为上位规则。

## 0. 上游资产配置 Scope

`skills/a-share-multi-asset-allocation/` 位于股票账户之前，负责把：

```text
Total Financial Assets
→ Liquidity / Liability Reserve
→ Fixed Income
→ Equity Account Equity
```

它只决定**多少长期风险资本进入股票账户**，不覆盖股票账户内部的 Level 1A 规则。

一旦资金进入：

```text
Equity Account Equity / Stock Account Equity
```

长期/短中期比例、Final Short Cap、单股/风险簇、策略批次、回撤和账户级风险全部由 `capital-allocation-and-entry-policy.md` 管理。

因此：

```text
Multi-Asset Allocation Skill
!= 可以绕过 Stock Account Capital/Risk Policy 的更高权限
```

若两者发生边界冲突，先停止新增风险并标记 `Policy Conflict`，统一分母和 scope 后再执行。

## 1. 规则层级

```text
Level 1A — shared/capital-allocation-and-entry-policy.md
Level 1B — shared/automation-execution-governance.md
Level 1C — shared/research-model-governance.md
  ↓
Level 2  — skills/*/SKILL.md
  ↓
Level 3  — skills/*/references/*.md
           research/*.md
  ↓
Level 4  — examples / case studies / dated snapshots / watchlists
```

Level 1A、1B、1C 管不同维度：

- 1A：资本配置、统一分母、仓位、风险、建仓、补仓、止损/止盈、再平衡、账户级同股/风险簇聚合；
- 1B：Paper/Live、Broker Net Position、Strategy Virtual Position、执行安全、幂等、Kill Switch、合规和自动化晋级；
- 1C：研究证据等级、Champion/Challenger、point-in-time、Benchmark、模型验证与晋级。

多个 Level-1 同时涉及一个动作时必须同时满足，不能用研究模型、自动化规则或下层文件绕过资本/风险上限。

## 2. Level 1A — Capital / Risk

`shared/capital-allocation-and-entry-policy.md` 是以下事项唯一 Source of Truth：

- `Stock Account Equity` 统一分母；
- 长期 / 短中期资金分配；
- Size Cap / Risk Cap / Edge Cap / Final Short Cap；
- Operating Target / Hard Ceiling；
- 长期/短中期策略批次；
- 账户级单股与风险簇上限；
- 长期+短中期同股/同因子合计暴露；
- `CAP_BREACH`；
- 跨策略再平衡和利润回流；
- 回撤熔断；
- 大资金流动性约束。

任何下层文件不得放宽这些限制。

## 3. Level 1B — Automation / Execution

`shared/automation-execution-governance.md` 管理：

- Research → Paper → Manual Live → Assisted → Semi-auto → Auto；
- `AUTO_ORDER=false` 默认状态；
- `paper_capital_rmb` 与 `reporting_nav` 分离；
- Broker Net Position / Strategy Virtual Position；
- cross-strategy order conflict / netting；
- reconciliation；
- idempotency / duplicate-order protection；
- fail closed / Kill Switch；
- 程序化交易与券商合规；
- Governance Bundle 的执行记录；
- 凭据安全；
- 自动化系统不得自行改 policy / Skill / Champion。

各策略 roadmap 可以更保守，不能绕过本规则。

## 4. Level 1C — Research / Model

`shared/research-model-governance.md` 管理：

- Fact / Research-supported Principle / Governance Parameter 分层；
- Champion/Challenger；
- Shadow score 与模型晋级；
- point-in-time、look-ahead、幸存者偏差；
- Benchmark 口径；
- Required Return / Risk Premium 参数治理；
- Expected IRR 方法的研究治理；
- MFE/MAE 学习闭环；
- 参数修改留痕；
- Model Promotion 与 Automation Promotion 分离。

任何新评分权重、退出阈值、因果模型或特征组合，在正式 Promotion 前都只是 Challenger / Research Proposal，不得静默覆盖生产模型。

## 5. Level 2 — Skills

`skills/*/SKILL.md` 定义各策略生产领域规则：

- 一级资产配置的上游范围与输出；
- 选股 / 评分 / 估值 / 入场条件；
- 持仓状态；
- 领域专用风险逻辑；
- 输出合同；
- 本策略特有研究与执行流程。

Skill 可比 Level 1 更保守，不可更激进。

## 6. Level 3 — References 与 Research Workspace

### Skill references

`skills/*/references/*.md` 用于解释、展开和模板化 Skill，包括：

- methodology；
- execution template；
- holding/risk management；
- scoring；
- data source policy；
- research basis；
- Sentiment Regime Index；
- Challenger model；
- Champion/Challenger Forward-Test；
- Expected IRR / Benchmark；
- automation roadmap；
- validation ledger。

### Top-level `research/`

`research/*.md` 用于跨策略研究协议、实证计划和实验设计，例如长期 vs 短中期 Forward Study。

它们是**研究协议，不是生产 Policy 或 Skill**：

- 可以定义实验 cohort、指标和对照组；
- 可以提出 Challenger / hypothesis；
- 不能修改资金上限、生产评分、下单权限；
- 不能因研究结果好看自动触发 Promotion；
- 若与 Level 1/2 冲突，以 Level 1/2 为准。

因此 `ACTIVE FORWARD STUDY` 只表示研究正在进行，不等于生产策略规则已经改变。

## 7. Level 4 — Examples / Case Studies / Snapshots

以下均为**非规范性证据记录**：

- `examples/` 下模型组合、case study、JSON baseline；
- 带日期 snapshot/watchlist；
- 历史候选池；
- forward-test 历史起点。

规则：

- 不能覆盖当前 policy / Skill；
- 不是永久推荐名单；
- 历史价格、分红、评分和权重不能直接当当前事实；
- 真实买入必须 fresh run；
- 当时已公开但记录错误的事实可做明确 correction/errata；
- 不得用未来数据静默改写过去判断。

## 8. Operating Target / Hard Ceiling

```text
Operating Target = 日常默认目标
Hard Ceiling      = 计划风险绝对上限
```

具体数值只在 Level 1A 保存。

Hard Ceiling 是计划风险限制，不是 gap/跌停下实际成交亏损保证。

## 9. 策略批次 ≠ 执行拆单

- **策略批次**：新的投资/交易判断得到事实或价格确认；
- **执行拆单**：为了流动性、滑点、冲击成本把同一策略批次拆成多个订单。

策略批次只从 Level 1A 读取。执行拆单不能伪装成新策略确认。

## 10. Model Promotion ≠ Automation Promotion

```text
Good Model != Safe Auto Execution
Safe Executor != Positive Edge
```

只有研究模型通过 Level 1C、执行系统通过 Level 1B、实际仓位通过 Level 1A，才允许提高真实自动化程度。

## 11. Governance Bundle

Paper cohort、生产决策和订单至少记录：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version
model_version
```

禁止只保存一个含义不明的 `policy_version`。

## 12. 参数 / 架构更新规则

任何 Level-1 或生产 Champion 变更必须同步检查：

1. 根 `README.md`；
2. 三个 Skill README / `SKILL.md`；
3. methodology / holding / execution-template / scoring / sentiment；
4. research-basis / research-validation / adversarial research review；
5. `research/*.md` 跨策略研究协议；
6. Champion/Challenger / IRR / Benchmark / validation ledgers；
7. automation roadmaps / runtime monitor；
8. examples README / case-study 声明；
9. evaluation cases；
10. consistency audit。

历史快照原则上不追溯重写；事实错误按 correction 规则处理。

## 13. 冲突处理

```text
Level 1 优先
更高层优先
更保守优先
事实优先于预测
当前 policy 优先于历史 example/snapshot
当前 Champion 优先于未晋级 Challenger
Broker 实际成交/持仓优先于本地假设
```

同级但不同维度的规则必须同时满足。

若无法判断冲突：

```text
Policy Conflict
→ 停止相关新风险动作
→ 修正规则
→ 再执行
```
