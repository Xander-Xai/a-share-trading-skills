# Session-aware A-share Execution Calendar v1

> Status: `ACTIVE EXECUTION FACT CONTRACT`
>
> Purpose: determine the earliest legally and operationally executable timestamp after new information becomes public. This is an execution/PIT contract, not an alpha feature.

## 1. Current rule snapshot

Rule snapshot checked on `2026-08-28` against the current Shanghai and Shenzhen exchange trading rules.

For current A-shares, the exchange session model includes:

```text
Opening auction / continuous auction / closing auction
15:00 close
15:05–15:30 post-close fixed-price trading, subject to exchange eligibility and suspension state
```

Current official references:

- SSE 2026 Trading Rules: https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml
- SZSE 2026 Trading Rules PDF: https://docs.static.szse.cn/www/lawrules/rule/trade/current/W020260424690713155663.pdf

The repository must re-check current exchange rules before Live/Semi-auto/Auto execution. This snapshot must not be assumed permanent.

## 2. Three timestamps, not one

For each material event preserve:

```text
information_timestamp
first_exchange_tradable_timestamp
first_broker_executable_timestamp
```

Then define:

```text
first_tradable_timestamp
= max(
    information_timestamp + minimum decision/data latency,
    first_exchange_tradable_timestamp,
    first_broker_executable_timestamp
  )
```

If broker support or exchange eligibility is unknown:

```text
first_tradable_timestamp = UNRESOLVED
position_state = FLAT
```

Do not assume an exchange session automatically implies the user's broker/account can execute it.

## 3. Session-routing logic

### Event before or during normal auction/continuous trading

Use the first future executable auction/continuous-trading window after the information is public and the decision can be formed.

Do not backdate a signal to a price printed before the information timestamp.

### Event after 15:00 but before/during the post-close fixed-price window

Do **not** automatically set `first_tradable_timestamp = next trading day`.

Check in order:

```text
1. Is the security eligible for post-close fixed-price trading under current exchange rules?
2. Was it still suspended at 15:00?
3. Is the current timestamp still inside a valid order/transaction window?
4. Does the broker/account support the relevant order type?
5. Is there executable liquidity under the fixed-price mechanism?
6. Can the information be ingested and the decision formed before the usable window closes?
```

If all pass, the first tradable timestamp may be in the same-day post-close session.

If any required state is unknown, mark `UNRESOLVED` and fail closed.

### Event after the usable post-close window

Earliest execution is the next valid trading session, subject to suspension/holiday/price-limit/broker constraints.

### Event published while suspended

Do not infer a tradable timestamp from the publication time alone. Resolve suspension status and the next exchange-eligible session.

## 4. Price used for research versus executable price

Preserve separately:

```text
pre_event_reference_price
last_pre_event_market_price
first_post_event_market_price
planned_order_price
simulated_fill
actual_fill
```

A same-day closing price that occurred before an after-close disclosure cannot be labeled a post-event reaction.

A post-close fixed-price fill, if available, must not be confused with the 15:00 closing-auction reaction because the information set differs.

## 5. Reaction-window anchor

ERG reaction windows must anchor to the first market window that could legally incorporate the event for the strategy:

```text
reaction_anchor = first_tradable_timestamp/session
```

Record the session type:

```text
OPEN_AUCTION
CONTINUOUS_AM
CONTINUOUS_PM
CLOSING_AUCTION
POST_CLOSE_FIXED_PRICE
NEXT_SESSION
UNRESOLVED
```

Do not mix post-close and next-day reactions without preserving the session label.

## 6. A-share execution constraints that still apply

Session routing does not override:

- T+1 constraints for ordinary newly purchased A-shares;
- price limits;
- suspension/resumption;
- 100-share execution units where applicable;
- commission/tax/slippage/market impact;
- broker permissions and order-type support;
- account-level risk/position caps;
- `CAP_BREACH` and circuit breakers.

## 7. Required fields

Event-driven records add:

```text
exchange
board
session_rule_version
session_type
post_close_eligible
suspension_state_at_1500
broker_post_close_support
information_timestamp
first_exchange_tradable_timestamp
first_broker_executable_timestamp
first_tradable_timestamp
first_tradable_resolution_status
```

Allowed resolution status:

```text
RESOLVED
UNRESOLVED_EXCHANGE_RULE
UNRESOLVED_SUSPENSION
UNRESOLVED_BROKER_SUPPORT
UNRESOLVED_LIQUIDITY
OUTSIDE_SESSION
```

## 8. Validation cases

At minimum preserve regression cases for:

```text
A. event at 14:30
B. event at 15:02
C. event at 15:08
D. event at 15:29
E. event at 15:31
F. event at 16:23
G. event while security is suspended at 15:00
H. broker does not support post-close order type
```

Expected behavior is session resolution, not a buy/sell recommendation.

## 9. Governance

This file fixes execution/PIT semantics only.

It does not change:

```text
Champion weights
ERG Shadow status
risk caps
position sizing
entry tranche rules
```

Any future exchange-rule change requires a version bump and a regression audit of historical `first_tradable_timestamp` calculations.