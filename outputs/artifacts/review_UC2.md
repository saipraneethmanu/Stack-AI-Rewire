# Memo review: UC2 ice-cream sales, weather and holidays

Reviewer: Sai Praneeth. Memo reviewed: `outputs/UC2/feasibility_memo.md`, checked against `outputs/UC2/records/`, `risk_assessment.json` and `trace.jsonl`.

## Where I agree
- **Overall: not feasible as scoped.** Agree. N2 (the mapping of product codes across the 2024-04-01 code change) is a must need with no source. The wiki page `product_codes_2024` says no mapping table exists.
- **`internal.sales.products` cannot serve N2.** Agree. It lists current codes only, so it has no old-to-new history to map against.
- **Sales access is restricted.** Agree. The catalog says request to Retail Operations, and nothing was sampled.
- **Holiday data: national only.** Agree. Local patron-saint days are not covered by any register source.

## Where I overrule the pipeline, and why
1. **N4 holidays: a blocker with no named owner is rated feasible with conditions.** `api.nager_public_holidays` carries LIC-UNKNOWN, a blocker. Calibration rule 2 allows feasible with conditions only when a named person can clear it. The condition asks for "Legal confirms", with no named party and no owner recorded. Under rule 1 this should be not feasible for N4. N4 is a should need, so the overall verdict is unchanged, but the source verdict should be corrected. Recorded as an override in review only.
2. **Open-Meteo shop coordinates.** The memo says "shop coordinates not chosen". The register default for `api.open_meteo_archive` is 45.46, 9.19, which I set for UC1 as a northern-Italy placeholder. The shop's city is not named in any source, so this placeholder is shared by both use cases. The memo should say the coordinates are a placeholder until the owner confirms the shop's location.
3. **Copernicus terms.** The memo rates the weather source feasible with conditions and lists the Copernicus terms as unread. I agree, and I did not read them either. This is a condition, not a finding I can close here.

## Verdict per source
| Source | Need | Pipeline verdict | My verdict |
|---|---|---|---|
| internal.sales.daily_by_product | N1 | feasible with conditions | feasible with conditions (Retail Operations approval; refund and VAT treatment) |
| internal.sales.products | N2 | not feasible | not feasible |
| internal.store.calendar | N5 | feasible with conditions | feasible with conditions (row completeness; undocumented `is_open` and `event_name`) |
| api.open_meteo_archive | N3 | feasible with conditions | feasible with conditions, coordinates as placeholder |
| api.nager_public_holidays | N4 | feasible with conditions | not feasible until a licence owner is named (see overrule 1) |

## Gate decision
Stop. The must need N2 has no source and no path to one that I can see. Stopping is the outcome the brief allows for an unmet must need. Revisit when Retail Operations confirms whether a pre/post-2024 code mapping exists.

## Memo conclusion traced
"N2 is unmet. No mapping exists in any source." Traced to `internal.sales.products`, field `temporal.grain` (static, current codes only), and the wiki page `product_codes_2024`.
