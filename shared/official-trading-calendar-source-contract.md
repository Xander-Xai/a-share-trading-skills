# Official Trading Calendar Source Contract v1

> Status: `ACTIVE DATA SOURCE CONTRACT`
>
> Scope: shared market infrastructure for both `long` and `short_mid` sleeves.

## 1. Purpose

This contract defines how an official annual SSE/SZSE trading-calendar plan is converted into canonical `TRADING_SESSION` facts and a PIT-visible completeness assertion.

The calendar is shared factual infrastructure. It is **not** a Short/Mid signal and it does not authorize orders.

## 2. Official 2026 sources

### SSE

Annual closure notice:

`https://www.sse.com.cn/disclosure/announcement/general/c/c_20251222_10802507.shtml`

Current 2026 trading rule reference:

`https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml`

### SZSE

Annual closure notice:

`https://www.szse.cn/disclosure/notice/general/t20251222_618087.html`

Current 2026 trading rule reference:

`https://docs.static.szse.cn/www/lawrules/rule/trade/W020260424690713155663.pdf`

The exchange rules define ordinary trading days as Monday through Friday, with statutory holidays and exchange-announced closure days closed.

## 3. No undocumented live endpoint

v1 intentionally does **not** reverse engineer or freeze an undocumented JSON endpoint.

The approved current path is:

```text
official notice + official trading-rule fact
→ reviewed machine-readable annual plan
→ OfficialAnnualTradingCalendarPlan
→ TRADING_SESSION rows
→ DATASET_COVERAGE(TRADING_SESSION)
→ PITStore
```

A later live transport may replace the reviewed plan only after its acquisition contract, raw-evidence archival and permitted-use status are reviewed.

## 4. Date-only publication handling

The annual 2026 notices expose a publication date but the repository has not frozen a reliable intra-day publication timestamp.

Therefore v1 uses a conservative visibility rule:

```text
publication_date = 2025-12-22
available_at     = 2025-12-23 00:00 Asia/Shanghai
```

This does not claim the notice was actually first visible at midnight. It deliberately delays visibility until the next calendar day so historical replay cannot invent an earlier intra-day timestamp.

## 5. Enumeration semantics

For each exchange/year, v1 enumerates every calendar date:

```text
weekday Monday-Friday
AND not inside an official annual closure range
→ is_open = true

otherwise
→ is_open = false
```

The output is one canonical row per date:

```text
TRADING_SESSION
exchange
trade_date
is_open
session_rule_version
```

For 2026 there are 365 rows per exchange.

## 6. Coverage assertion

Once the annual plan is validated, the adapter also emits:

```text
dataset_family       = TRADING_SESSION
scope_type           = EXCHANGE
start_date           = YYYY-01-01
end_date             = YYYY-12-31
completeness_status  = CONFIRMED_COMPLETE
verification_method  = EXCHANGE_CALENDAR_ENUMERATION
expected_count       = 365/366
observed_count       = 365/366
```

This assertion proves that the annual plan enumerated every calendar date in the configured year. It does not prove that no later emergency or ad-hoc exchange closure occurred.

## 7. Emergency / ad-hoc closure rule

If an exchange later announces an emergency or ad-hoc closure that changes a previously enumerated date:

```text
old TRADING_SESSION revision
→ new PIT revision
→ old annual coverage must not be treated as the final truth for the affected replay state
```

The new evidence must carry a later `available_at`, source lineage and revision relationship.

The current v1 annual plan is therefore safe for scheduled-calendar coverage but remains revisionable.

## 8. Source lineage and license boundary

Current checked-in plans use explicit source URLs and a curated `source_snapshot_id`.

They are not represented as immutable raw HTTP captures.

Default:

```text
source_tier    = TIER1
permitted_use  = UNRESOLVED_LICENSE
```

Therefore:

```text
TIER1 authority
!= permission for unrestricted production/redistribution
```

A future raw capture should use `RawEvidenceArchive` and replace the curated source snapshot identifier with the resulting `raw_snapshot_id`.

## 9. Strategy boundary

The following are shared facts:

```text
TRADING_SESSION
exchange closures
calendar coverage
```

The following remain Short/Mid-only consumers:

```text
5/10/20-session return
MA / RVOL
gap / execution geometry
Champion / ERG
```

Long-term methodology does not inherit tactical holding periods, R-based stops or short-horizon confirmation rules merely because both sleeves use the same exchange calendar.

## 10. Promotion boundary

This source contract may be used for research replay after tests pass.

It does not by itself promote:

```text
broker execution
AUTO_ORDER
Champion alpha
ERG alpha
```

Those remain separately governed.
