# Repository Policy Precedence

> 本文件定义全仓库规则层级。涉及资金/风险数值，以 `capital-allocation-and-entry-policy.md` 为唯一 Source of Truth；涉及模拟仓、券商执行和自动化安全，以 `automation-execution-governance.md` 为跨策略上位规则；涉及 Champion/Challenger、point-in-time、Benchmark、模型晋级与研究参数证据等级，以 `research-model-governance.md` 为跨策略研究治理规则。

## 1. 规则层级

当多个文件对同一问题给出不同规则时，按以下顺序执行：

```text
Level 1A — shared/capital-allocation-and-entry-policy.md
Level 1B — shared/automation-execution-governance.md
Level 1C — shared/research-model-governance.md
  ↓
Level 2  — skills/*/SKILL.md
  ↓
Level 3  — skills/*/references/*.md
  ↓
Level 4  — examples / case studies / dated snapshot / watchlist
```

Level 1A、1B、1C 管理不同维度：

- 1A：资本配置、仓位、风险、建仓、补仓、止损/止盈、再平衡；
- 1B：Paper/Live 模式、执行安全、对账、幂等、Kill Switch、合规和自动化晋级；
- 1C：研究证据等级、Champion/Challenger、point-in-time、Benchmark、模型验证与晋级。

若多个 Level-1 文件涉及同一动作，必须同时满足；不存在用研究模型、自动化规则或下层 reference 绕过资金风险上限的情况。

## 2. Level 1A：仓库级资本与风险规则

`shared/capital-allocation-and-entry-policy.md` 是以下事项的唯一 Source of Truth：

- 长期 / 短中期资金分配；
- Size Cap / Risk Cap / Edge Cap；
- Operating Target / Hard Ceiling；
- 长期与短中期默认策略批次；
- 动态单股与风险簇上限；
- 跨策略再平衡和利润回流；
- 账户级回撤熔断；
- 大资金流动性约束。

任何下层文件都不得放宽这些限制。

## 3. Level 1B：跨策略自动化与执行治理

`shared/automation-execution-governance.md` 是以下事项的跨策略上位规则：

- Research → Paper → Manual Live → Assisted → Semi-auto → Auto 的晋级顺序；
- `AUTO_ORDER=false` 的默认状态；
- Paper 执行本金与标准化 NAV 的分离；
- broker position reconciliation；
- 订单幂等与重复订单防护；
- fail closed / Kill Switch；
- 程序化交易与券商合规门禁；
- 自动化运行时最低审计字段；
- 凭据不得进入仓库；
- 自动化系统不得自行修改 policy/Skill。

长期和短中期各自的 roadmap 可以增加更保守的门槛，但不能绕过本规则。

## 4. Level 1C：跨策略研究与模型治理

`shared/research-model-governance.md` 是以下事项的跨策略研究上位规则：

- Fact / Research Principle / Governance Parameter 的证据分层；
- Champion/Challenger 双轨；
- Shadow score 与模型晋级；
- point-in-time、look-ahead、幸存者偏差治理；
- Benchmark 口径；
- Required Return / ERP 参数治理；
- MFE/MAE 学习闭环；
- 模型参数修改留痕；
- Model Promotion 与 Automation Promotion 分离。

任何新评分权重、退出阈值、因果模型或特征组合，在没有完成晋级流程前都只是 Challenger，不得静默覆盖生产模型。

## 5. Level 2：各 Skill 的领域规则

`skills/*/SKILL.md` 负责定义：

- 选股 / 评分 / 估值 / 入场条件；
- 持仓状态；
- 领域专用风险逻辑；
- 输出格式；
- 本策略特有的研究和执行流程。

Skill 可以比 shared 更保守，但不能更激进。

## 6. Level 3：References

References 用来解释、展开、模板化 Skill 规则，例如：

- methodology；
- execution template；
- holding/risk management；
- scoring；
- data source policy；
- research basis；
- Challenger model；
- Champion/Challenger Forward-Test；
- IRR / Benchmark framework；
- automation roadmap；
- validation metrics。

若 reference 与 shared 或 SKILL 冲突，reference 自动失效，以更高层规则为准。

特别说明：即使某个 roadmap 或 Challenger 位于 `references/`，它仍然只是设计/研究说明，不得覆盖 Level 1 或当前 Champion。

## 7. Level 4：Examples / Case Studies / Snapshots

以下内容全部视为**非规范性证据记录**：

- `examples/` 下的模型组合、case study、JSON baseline；
- 带日期的 `snapshot` / `watchlist`；
- 历史候选池；
- forward-test 起点。

规则：

- 不能覆盖当前 policy；
- 不能被视为永久推荐名单；
- 历史价格、分红、评分、权重不能直接当作当前事实；
- 后续真实买入必须重新运行对应 Skill；
- 若发现“当时已公开但记录错误”的事实，可做明确 correction/errata，并保留修订原因；
- 不得用未来数据静默改写过去判断。

## 8. Operating Target 与 Hard Ceiling

```text
Operating Target = 日常默认目标
Hard Ceiling      = 绝对不能突破的上限
```

具体数值只在 `capital-allocation-and-entry-policy.md` 保存。

下层文件可以更保守，但 Hard Ceiling 永远由 Level 1A 决定。

## 9. 策略批次 ≠ 执行拆单

- **策略批次**：新的投资/交易判断得到事实或价格确认；
- **执行拆单**：为了流动性、滑点和冲击成本，把同一策略批次拆成多个订单。

策略批次只从 Level 1A 读取。执行拆单数量可以变化，但不能被误记为新策略判断。

## 10. Model Promotion ≠ Automation Promotion

```text
研究模型更好
!=
自动执行已经安全
```

以及：

```text
自动执行可靠
!=
策略拥有正 Edge
```

只有研究模型通过 Level 1C、执行系统通过 Level 1B、实际仓位同时满足 Level 1A，才允许提高真实自动化程度。

## 11. 参数 / 架构更新规则

任何 Level-1 规则发生修改，必须同步检查：

1. 根 `README.md`；
2. 两个 `SKILL.md` / 对应 README；
3. methodology / holding / execution-template / scoring 等相关 references；
4. research-basis / research-validation / adversarial research review；
5. Champion/Challenger / IRR / Benchmark / validation ledgers；
6. automation roadmaps / validation ledgers；
7. examples README 与 case-study 声明；
8. evaluation cases；
9. 当前 consistency audit。

历史快照原则上不追溯重写，但必须明确其历史属性；事实错误按 correction 规则处理。

## 12. 冲突处理原则

```text
Level 1 优先
更高层优先
更保守优先
事实优先于预测
当前 policy 优先于历史 example/snapshot
当前 Champion 优先于未晋级 Challenger
broker 实际成交/持仓优先于本地假设
```

若无法判断冲突，停止相关执行动作并标记：

```text
Policy Conflict
```

先修正规则，再给出仓位、订单或自动化执行建议。
