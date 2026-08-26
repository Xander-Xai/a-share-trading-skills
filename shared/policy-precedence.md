# Repository Policy Precedence

> 本文件定义整个仓库的规则优先级，用于避免不同 Skill、reference、历史快照之间出现新旧理论冲突。

## 1. 唯一优先级

当多个文件对同一问题给出不同规则时，按以下顺序执行：

```text
Level 1 — shared/capital-allocation-and-entry-policy.md
  ↓
Level 2 — skills/*/SKILL.md
  ↓
Level 3 — skills/*/references/*.md
  ↓
Level 4 — *snapshot-YYYY-MM-DD.md / *watchlist-YYYY-MM-DD.md
```

### Level 1：仓库级资本与风险规则

`shared/capital-allocation-and-entry-policy.md` 是以下事项的唯一 Source of Truth：

- 长期 / 短中期资金分配
- Size Cap / Risk Cap / Edge Cap
- 单笔和组合风险预算的硬上限
- 长期与短中期的默认建仓批次
- 跨策略再平衡和利润回流
- 账户级回撤熔断
- 大资金流动性和执行约束

任何下层文件都不得放宽 Level 1 的风险限制。

### Level 2：各 Skill 的领域规则

`skills/*/SKILL.md` 负责定义各自策略的：

- 选股 / 评分 / 估值 / 入场条件
- 持仓状态
- 领域专用风险逻辑
- 输出格式

Skill 可以比 shared 更保守，但不能更激进。

### Level 3：Reference

reference 用来解释、展开、模板化 Skill 规则。若 reference 与 SKILL 或 shared 冲突，reference 自动失效，以更高层规则为准。

### Level 4：历史快照

带日期的 snapshot / watchlist 只用于回溯当时研究结果：

- 不能覆盖当前 policy；
- 不能被视为永久推荐名单；
- 不能把历史价格、分红、评分、仓位直接当作当前事实。

## 2. 风险参数的两层语义

短中期交易同时区分：

```text
Operating Target = 日常默认目标
Hard Ceiling      = 绝对不能突破的上限
```

当前默认：

```text
Operating Target
- 单笔计划风险：0.5% × 短中期策略净值
- 全部未平仓初始风险：2%
- 单一行业/因子初始风险：1%

Hard Ceiling
- 单笔计划风险：1%
- 全部未平仓初始风险：3%
```

只有在策略 Edge 已被充分验证、市场环境和 setup 质量都较好时，单笔风险才允许从 0.5% 向 1% 靠近；任何时候都不得突破 Hard Ceiling。

## 3. 策略批次 ≠ 执行拆单

必须区分：

- **策略批次**：一次新的投资/交易判断是否被事实或价格确认；
- **执行拆单**：为了流动性、滑点和冲击成本，把同一策略批次拆成多个订单。

例如短中期默认策略批次仍是：

```text
50% Setup + 50% Confirmation
```

即使一笔 50% 的策略批次为了成交被拆成 4 个订单，也不等于策略变成 4 批。

## 4. 参数更新规则

任何仓库级风险参数修改时，必须同步检查：

1. 根 `README.md`
2. 两个 `SKILL.md`
3. 相关 holding / methodology / execution-template
4. research-basis / research-validation
5. evaluation cases

历史 snapshot 不追溯修改，但必须保留“历史快照，不覆盖当前政策”的声明。

## 5. 冲突处理原则

```text
更高层优先
更保守优先
更新版本优先
事实优先于预测
当前政策优先于历史快照
```

若无法判断冲突，应停止执行相关动作并标记 `Policy Conflict`，先修正规则再下单或给出仓位建议。
