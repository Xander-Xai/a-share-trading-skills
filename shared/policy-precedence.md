# Repository Policy Precedence

> 本文件定义全仓库规则层级与实现边界。任何增加**真实资金**股票风险的动作首先受 Level 0 资金资格与订单授权硬门禁约束；通过后，资金/风险以 `capital-allocation-and-entry-policy.md` 为股票账户内 Source of Truth。Paper 使用隔离的 paper capital 与相同风险数学，但不伪造个人资金 Gate；Paper/Broker/自动化以 `automation-execution-governance.md` 为上位规则；研究证据、Champion/Challenger、point-in-time、Benchmark 与模型晋级以 `research-model-governance.md` 为上位规则。

## 0. 上游资产配置 Scope

`skills/a-share-multi-asset-allocation/` 位于股票账户之前：

```text
Total Financial Assets
→ Liquidity / Liability Reserve
→ Fixed Income
→ Stock Account Equity
```

它只决定**多少长期风险资本成为 Stock Account Equity**，不覆盖股票账户内部 Level 1A。

进入 Stock Account Equity 后：

```text
Stock Account Equity
→ Long Strategic Baseline
+ Short/Mid Final Cap
+ Stock-account Pending Cash
```

长期/短中期比例、Final Short Cap、账户级单股/风险簇、策略批次、回撤和跨策略风险全部由 Level 1A 管理。

因此：

```text
Multi-Asset Allocation Skill
!= 可以绕过 Stock Account Capital/Risk Policy 的更高权限
```

Scope 或分母无法统一时：

```text
Policy Conflict
→ 停止新增风险
→ 统一口径
→ 再执行
```

## 1. 规范性规则层级

```text
Level 0  — shared/capital-eligibility-and-investor-risk-philosophy.md
           shared/pre-trade-order-authorization-contract.md
  ↓
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

- 0：真实资金是否有资格承担股票风险、是否允许输出真实可执行买入股数、强制个人资金问卷、ENTRY/ADD 授权；对真实新增风险拥有 Hard Veto；
- 1A：资本配置、统一分母、仓位、风险、建仓、补仓、止损/止盈、再平衡、账户级同股/风险簇聚合；
- 1B：Paper/Live、Broker Net Position、Strategy Virtual Position、执行安全、幂等、Kill Switch、合规和自动化晋级；
- 1C：研究证据等级、Champion/Challenger、point-in-time、Benchmark、模型验证与晋级。

真实资金增加风险时 Level 0 必须先通过；通过后，多个 Level-1 同时涉及一个动作时必须全部满足。Paper 不采集个人财务 Gate，但必须使用 paper capital 并通过适用的 Level 1A / 1B 风险与执行约束。

## 1A. Level 0 — Capital Eligibility / Pre-Trade Authorization

Level 0 由以下两个文件共同构成：

- `shared/capital-eligibility-and-investor-risk-philosophy.md` — 判断什么钱有资格进入股票风险；
- `shared/pre-trade-order-authorization-contract.md` — 在给出真实 ENTRY/ADD 股数前强制收集个人资金、账户暴露、风险预算与交易触发信息。

Level 0 是**真实资金新增风险**的最高优先级否决层：

```text
Level 0 FAIL / UNKNOWN critical field
→ research may continue
→ WATCH / READY allowed
→ executable ENTRY / ADD shares = 0
```

任何 Skill、Champion、估值模型、技术信号、人工 override 或自动化模块都不能绕过 Level 0 增加风险。

TRIM / EXIT 属于降低风险动作；在信息不完整但需要保护资本时，可以按既定风险计划继续执行，不应被 Level 0 阻止。

Multi-Asset Allocation 仍负责从 Total Financial Assets 生成可进入股票系统的长期风险资本；Level 0 不替代资产配置，而是在**每次证券级增加风险前再次授权**，防止个人现金需求或账户状态变化后仍按旧假设下单。

## 2. Level 1A — Capital / Risk

`shared/capital-allocation-and-entry-policy.md` 是 Stock Account Equity 内以下事项唯一 Source of Truth：

- `Stock Account Equity` 分母；
- 长期 / 短中期资金分配；
- Size Cap / Risk Cap / Edge Cap / Final Short Cap；
- Operating Target / Hard Ceiling；
- 长期/短中期策略批次；
- 账户级单股与风险簇上限；
- 长期+短中期同股/同因子合计暴露；
- `CAP_BREACH`；
- 跨策略再平衡和利润回流；
- 短中期回撤熔断；
- 大资金流动性约束。

任何下层文件不得放宽这些限制。

## 3. Level 1B — Automation / Execution

`shared/automation-execution-governance.md` 管理：

- Research → Paper → Manual Live → Assisted → Semi-auto → Auto；
- `AUTO_ORDER=false` 默认状态；
- `paper_capital_rmb` / `reporting_nav`；
- Broker Net Position / Strategy Virtual Position；
- cross-strategy order conflict / netting；
- reconciliation；
- idempotency / duplicate-order protection；
- fail closed / Kill Switch；
- 程序化交易与券商合规；
- Governance Bundle；
- 凭据安全；
- 自动化不得自行改 policy / Skill / Champion。

策略 roadmap 和 runtime 可以更保守，不能绕过本规则。

## 4. Level 1C — Research / Model

`shared/research-model-governance.md` 管理：

- Fact / Research-supported Principle / Governance Parameter 分层；
- Champion/Challenger；
- Shadow score 与模型晋级；
- point-in-time、look-ahead、幸存者偏差；
- Benchmark；
- Required Return / Risk Premium；
- Expected IRR 研究治理；
- MFE/MAE 学习闭环；
- 参数修改留痕；
- Model Promotion 与 Automation Promotion 分离。

任何新评分、退出阈值、情绪权重、因果模型或特征组合，在正式 Promotion 前均为 Challenger / Research Parameter，不得静默覆盖生产模型。

## 5. Level 2 — Skills

当前三个 Skill 分工：

```text
Multi-Asset Allocation Skill
→ Total Financial Assets 到 Stock Account Equity

Retirement Investing Skill
→ 长期股票研究、估值、Expected IRR、长期持仓

Short/Mid Stock Selection Skill
→ 短中期 Champion、入场、风险和持仓管理
```

`skills/*/SKILL.md` 可以比 Level 1 更保守，但不能放宽 Level 1。

## 6. Level 3 — References / Research Workspace

### Skill references

`skills/*/references/*.md` 用于解释和模板化生产 Skill，包括 methodology、scoring、sentiment、IRR/Benchmark、holding、validation、Challenger、roadmap 等。

### Top-level research

`research/*.md` 用于跨策略实证计划和实验协议，例如长期 vs 短中期 Forward Study。

它们可以：

- 定义 cohort、指标、Benchmark、对照组；
- 提出 hypothesis / Challenger。

但不能：

- 修改资金上限、生产评分或下单权限；
- 因结果好看自动 Promotion；
- 覆盖 Level 1/2。

`ACTIVE FORWARD STUDY` 只表示研究正在进行。

## 7. Level 4 — Examples / Snapshots

以下为非规范性历史证据：

- `examples/` 模型组合、case study、JSON baseline；
- dated snapshot/watchlist；
- 历史候选池；
- forward-test 起点。

它们：

- 不能覆盖当前 policy / Skill；
- 不是永久推荐名单；
- 历史价格/分红/评分/权重不能直接当当前事实；
- 实盘前必须 fresh run；
- 当时已公开但记录错误可做 correction/errata；
- 不得用未来数据静默改写过去。

## 8. Runtime / Workflow — 实现层，不是规则层

以下属于**Implementation Layer**：

```text
runtime/*.py
runtime/tests/*
.github/workflows/*
```

规则：

- runtime 必须实现当前 Level 0 + Level 1 + 当前生产 Skill/Champion；
- 代码中的阈值若来自 research reference，必须明确其 research/governance parameter 身份；
- runtime 不能因为实现方便自行修改生产语义；
- `.github/workflows/` 只是编排执行，不获得新的策略权限；
- 当前 Daily Monitor 为 `MONITOR_ONLY`、`AUTO_ORDER=false`；
- 代码与文档冲突时，不以“代码已经这样写了”为理由改变 Policy；先修实现或走正式 Promotion。

生成内容：

```text
reports/daily/*
runtime/state/*
```

属于**Generated Evidence / Runtime State**，不是 Policy、Skill 或永久推荐。

## 9. Operating Target / Hard Ceiling

```text
Operating Target = 日常默认目标
Hard Ceiling      = 计划风险绝对上限
```

具体数值只在 Level 1A 保存。

Hard Ceiling 是计划风险限制，不是 gap/跌停下最大实际亏损保证。

## 10. 策略批次 ≠ 执行拆单

- 策略批次：新的投资/交易判断得到事实或价格确认；
- 执行拆单：为流动性、滑点、impact 把同一策略批次拆成多个订单。

执行拆单不能伪装成新策略确认。

## 11. Model Promotion ≠ Automation Promotion

```text
Good Model != Safe Auto Execution
Safe Executor != Positive Edge
```

研究模型通过 Level 1C、执行系统通过 Level 1B、仓位通过 Level 1A，才允许提高真实自动化程度。

## 12. Governance Bundle

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

Monitor-only 报告可先记录 governance 引用路径；进入 Paper/Live 必须记录具体版本。

## 13. 参数 / 架构更新检查

任何 Level-1、生产 Skill 或 Champion 变更必须同步检查：

1. 根 `README.md`；
2. 三个 Skill README / SKILL；
3. methodology / holding / execution-template / scoring / sentiment；
4. research-basis / research-validation / adversarial research review；
5. `research/*.md`；
6. Champion/Challenger / IRR / Benchmark / validation ledgers；
7. automation roadmaps；
8. `runtime/` 与 `.github/workflows/`；
9. examples / snapshots 声明；
10. evaluation / unit tests；
11. consistency audit。

历史快照原则上不追溯重写；事实错误按 correction 规则处理。

## 14. 冲突处理

```text
Level 0 对真实新增风险拥有最高 Hard Veto
通过 Level 0 后，Level 1 优先
更高层优先
更保守优先（前提是不改变已定义的生产语义）
事实优先于预测
当前 policy 优先于历史 example/snapshot
当前 Champion 优先于未晋级 Challenger
Broker 实际成交/持仓优先于本地假设
```

若无法判断：

```text
Policy Conflict
→ 停止相关新增风险动作
→ 修正规则/实现
→ 再执行
```