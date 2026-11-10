## 1. Executive summary

Overall verdict: **not feasible as scoped.** Must need N2 (mapping of product codes across the 2024-04-01 code change) is unmet, and the overall rule makes any unmet must need a blocker.

Facts that drive this:

1. N2 is unmet. The wiki page `product_codes_2024` says no mapping table exists. The only product master (`internal.sales.products`) lists current codes only.
2. N1 (daily sales by product) and N3 (daily max temperature) are must needs. Both are met with conditions. The sales source has a catalog range from 2022-01-01 with no end date, refreshed daily.
3. Access to sales data is restricted (confidential, request to Retail Operations). Nothing has been sampled.
4. Licences for two must-need and should-need sources are not cleared. The holiday feed licence is unknown. The weather data mixes CC BY 4.0 with Copernicus terms that have not been read.
5. Coverage is unconfirmed for the 2023-06-01 history start. The archive start, the 2023 and 2025 holiday years and the shop's own calendar completeness have not been probed or checked.

The route to a positive verdict is for Retail Operations to supply or confirm a pre/post-2024 product code mapping. That mapping is not in any catalogued source. If it is delivered, the verdict would move to feasible with conditions. The overall rationale in the discovery output says the same.

## 2. Need coverage

| need id | need | priority | status | best source(s) | gap |
|---|---|---|---|---|---|
| N1 | Daily ice-cream sales by product | must | met with conditions | internal.sales.daily_by_product | Retail Operations approval needed. Refund and VAT treatment unknown. 2024-02-05 to 2024-03-10 is a till gap. |
| N2 | Mapping of product codes before and after the 2024 code change | must | **unmet** | none | No mapping exists in any source. sales.products has current codes only. |
| N3 | Daily maximum temperature | must | met with conditions | api.open_meteo_archive | Archive start before 2025 not probed. Shop coordinates not chosen. Copernicus licence not read. |
| N4 | Public holidays in Italy | should | met with conditions | api.nager_public_holidays | Data licence unknown. 2023 and 2025 not probed. National holidays only. |
| N5 | Shop opening days and local events | should | met with conditions | internal.store.calendar | Row completeness unconfirmed. Meaning of is_open and event_name undocumented. No other local-event source. |

## 3. Source assessments

### Feasible (no source reached this verdict outright)

None.

### Feasible with conditions

**api.nager_public_holidays** (N4, should)
- What it is: a public REST endpoint returning national public holidays for a year and country code. Probes for 2024 and 2026 returned HTTP 200, with 13 and 14 holidays. Moveable feasts are included.
- Verdict: feasible with conditions.
- Flags:
  - LIC-UNKNOWN (blocker). The only licence found is MIT, and it covers the software repository. The source says nothing confirms it applies to the holiday data.
  - GOV-OWNER-UNKNOWN (major). Owner and steward are null. The publisher is the Nager.Date open-source project.
  - INT-REPRESENTATIVENESS (minor, not a formal flag). Only national holidays are covered. Local patron-saint days are absent.
- Conditions: Legal confirms commercial production use of the data. Probe 2023 and 2025 to confirm the windows. Name an owner. Note that local feasts are not covered.

**api.open_meteo_archive** (N3, must)
- What it is: a gridded reanalysis API returning daily maximum 2 m temperature for a chosen latitude and longitude. It is one grid point per query, not a station.
- Verdict: feasible with conditions.
- Flags:
  - LIC-MIXED (major). The licence is CC BY 4.0 with Copernicus C3S reanalysis terms. The Copernicus terms were not read. Commercial use is unknown.
  - LIC-ATTRIBUTION (minor). Attribution and a link to the licence are required.
  - COV-GEO-MISMATCH (minor). No source names the shop's city. The probes used a Milan-area point (45.46, 9.19), which snapped to grid point 45.448154, 9.169279. A grid point is not the shop's local temperature.
  - FRS-METADATA-DATE-MISLEADING (minor). The licence page header is dated 2026-11-10. That is after as_of and describes the web page, not the data.
- Coverage: the recent-window end (2026-03-31) was confirmed by a probe of 2026-03-29 to 2026-03-31. The archive start has not been established, so the 2023-06-01 start is unconfirmed.
- Conditions: Legal reads the Copernicus terms. Attribution is applied. The archive start is probed. Shop coordinates are chosen and recorded, with timezone set explicitly. The register default coordinates are not to be used.

**internal.sales.daily_by_product** (N1 must; N2 linked but unmet)
- What it is: units sold and revenue in EUR per product code per day, from the till system, owned by Retail Operations. The catalog gives about 310,000 rows. Coverage starts 2022-01-01 with no end date. Refresh is daily.
- Verdict: feasible with conditions, for N1 only.
- Flags:
  - ACC-RESTRICTED (major). Confidential. Access requires a request to Retail Operations. Warehouse SQL only.
  - INT-JOIN-KEY-MISMATCH (major). Product codes ending in "L" were replaced from 2024-04-01. No mapping table exists.
  - GOV-CATALOG-WIKI-CONFLICT (major). The catalog implies one current code set. The wiki says pre-2024 codes exist in the sales data.
  - DQ-UNDOCUMENTED-SCHEMA (minor). Refund, void and VAT treatment of revenue_eur is unknown. Not sampled.
- Unreconciled: about 310,000 rows does not reconcile with about 64 products over about 4.8 years. This was noted but not conditioned.
- Conditions: access granted. Refund, void and VAT treatment confirmed. Code mapping supplied. Catalog corrected. 2024-02-05 to 2024-03-10 treated as missing, not zero.

**internal.store.calendar** (N5 should; also linked to N4 in the catalog, but the holiday feed is the N4 source)
- What it is: an internal daily calendar of whether the shop was open, and any local event name, for each date. Store Operations owns it. Refresh is weekly per the catalog. Coverage starts 2022-01-01 with no end date.
- Verdict: feasible with conditions, for N5 only.
- Flags:
  - DQ-UNDOCUMENTED-SCHEMA (major). No linked wiki page. event_name is free text. Closure reasons are undocumented. is_open for 2024-02-05 to 2024-03-10 is unknown.
  - DQ-METADATA-CONTRADICTION (minor). Catalog row count is about 1,500. Calendar days from 2022-01-01 to 2026-10-10 are about 1,750.
  - INT-DUPLICATE-SOURCE (minor, not a duplicate). No other opening-days source was found.
- Conditions: Store Operations documents the fields and confirms row completeness from 2023-06-01 to 2026-03-31. Confirm analytics-role access, which has not been tested.

### Not feasible

**internal.sales.products** (N2, must)
- What it is: a static product master with one row per current code. It holds product name and category, about 64 rows. Retail Operations owns it. Last refreshed 2025-03-31 per the catalog.
- Verdict: not feasible.
- Flags:
  - INT-NO-JOIN-KEY (major). It lists current codes only. Pre-2024 "L" codes have no key here.
  - COV-GRAIN-MISMATCH (minor). Grain is static, with no temporal coverage. It cannot show which codes existed before 2024-04-01.
- Notes: it cannot meet N2. Its names may serve as a reference for a name-based match, but only if old codes are supplied. The wiki says names are not always unique.

## 4. Red-flag register

| source_id | code | severity | evidence | raised by (rule or judgement) |
|---|---|---|---|---|
| api.nager_public_holidays | LIC-UNKNOWN | blocker | Only MIT licence found, for the software repo. No statement that it covers holiday data. | rule |
| api.nager_public_holidays | GOV-OWNER-UNKNOWN | major | Owner and steward null. Publisher is the open-source project. | judgement |
| api.nager_public_holidays | INT-REPRESENTATIVENESS | minor (not a formal flag) | National calendar only. Local feasts absent. | judgement |
| api.open_meteo_archive | LIC-MIXED | major | Copernicus C3S terms apply and were not read. Commercial use unknown. | rule |
| api.open_meteo_archive | LIC-ATTRIBUTION | minor | CC BY 4.0 attribution and link required. | rule |
| api.open_meteo_archive | COV-GEO-MISMATCH | minor | Shop location unnamed. Grid point is a proxy. | judgement |
| api.open_meteo_archive | FRS-METADATA-DATE-MISLEADING | minor | Licence page dated 2026-11-10, after as_of. Not a data date. | judgement |
| internal.sales.daily_by_product | ACC-RESTRICTED | major | Confidential. Auth required. Request via Retail Operations. | rule |
| internal.sales.daily_by_product | INT-JOIN-KEY-MISMATCH | major | Codes ending in "L" replaced from 2024-04-01. No mapping. | judgement |
| internal.sales.daily_by_product | GOV-CATALOG-WIKI-CONFLICT | major | Catalog implies one code set. Wiki says pre-2024 codes exist. | judgement |
| internal.sales.daily_by_product | DQ-UNDOCUMENTED-SCHEMA | minor | Refund, void and VAT treatment unknown. Not sampled. | judgement |
| internal.sales.products | INT-NO-JOIN-KEY | major | Current codes only. No mapping table. | judgement |
| internal.sales.products | COV-GRAIN-MISMATCH | minor | Static grain. No dated history. | judgement |
| internal.store.calendar | DQ-UNDOCUMENTED-SCHEMA | major | No wiki. event_name free text. is_open unknown for the till-gap period. | judgement |
| internal.store.calendar | DQ-METADATA-CONTRADICTION | minor | Row count about 1,500 vs about 1,750 calendar days. | judgement |
| internal.store.calendar | INT-DUPLICATE-SOURCE | minor (not a duplicate) | No other opening-days source found. | judgement |

## 5. Conditions and owners

| condition | source(s) | who can resolve it | blocking which need |
|---|---|---|---|
| Produce or confirm a pre/post-2024-04-01 product code mapping, or a name-based mapping with manual review | internal.sales.daily_by_product | Retail Operations | N2 (must); overall verdict |
| Grant access through the request process | internal.sales.daily_by_product | Retail Operations | N1 (must) |
| Confirm whether units and revenue are net of refunds and voids, and whether revenue includes VAT | internal.sales.daily_by_product | Retail Operations | N1 (must) |
| Confirm which codes appear in the sales table and correct the catalog description | internal.sales.daily_by_product, internal.sales.products | Retail Operations | N1, N2 |
| Treat 2024-02-05 to 2024-03-10 as missing, not zero | internal.sales.daily_by_product | Analytics (per wiki guidance) with Retail Operations confirmation | N1 |
| Confirm commercial production use of holiday data (MIT licence is for software only) | api.nager_public_holidays | Legal | N4 (should) |
| Probe 2023 and 2025 holiday years against both windows | api.nager_public_holidays | Project data engineer | N4 (should) |
| Name an accountable owner for the holiday feed | api.nager_public_holidays | Retail Operations or project sponsor | N4 (should) |
| Read Copernicus C3S terms and confirm commercial use | api.open_meteo_archive | Legal | N3 (must) |
| Apply attribution text and licence link in any output | api.open_meteo_archive | Project team | N3 (must) |
| Probe archive start to confirm it reaches 2023-06-01 | api.open_meteo_archive | Project data engineer | N3 (must) |
| Choose and record shop coordinates and timezone | api.open_meteo_archive | Shop owner (choice); project data engineer (recording) | N3 (must) |
| Document is_open and event_name; confirm completeness 2023-06-01 to 2026-03-31; state is_open for the till-gap period | internal.store.calendar | Store Operations | N5 (should) |
| Confirm analytics-role access | internal.store.calendar | Store Operations | N5 (should) |

## 6. Recommended next steps

1. Raise an access request with Retail Operations for internal.sales.daily_by_product. Ask in the same request for the pre/post-2024-04-01 product code mapping, the refund and VAT treatment, and the list of product codes in the sales table.
2. Ask Retail Operations whether a mapping exists outside the catalogued sources. The wiki says none does. This is the single item that would change the overall verdict.
3. Ask Legal to confirm in writing whether the holiday data may be used commercially. Ask Legal to read the Copernicus C3S terms that apply to the weather data.
4. Ask Store Operations to document is_open and event_name, confirm row completeness for the history and recent windows, and grant analytics access.
5. Decide the shop's location for weather queries and record it in the project decisions file. Then probe the archive start date.
6. Probe the 2023 and 2025 holiday years.
7. Name an owner for the holiday feed.
8. Once the gate is passed (the N2 mapping, access and licences cleared), profile first: the sales table's code set before and after 2024-04-01, the till-gap days, and the revenue fields. Then profile the calendar row count and the weather archive start.

## 7. Open questions for the human reviewer

1. Does Retail Operations hold a pre/post-2024 product code mapping outside the catalogued sources? The wiki says none exists. If it does, who owns it?
2. Is N2 truly a gate for the whole use case? Or can the owner accept a reduced scope: comparing only products whose codes did not change, or only post-2024-04-01 history? The brief's second decision question asks which products can be compared. This needs a scope decision.
3. Which city or coordinates should represent the shop for weather? No source names it. Is a grid point acceptable as a proxy for the shop's temperature?
4. Who is the accountable owner for the public holiday feed? Is Legal's sign-off enough?
5. Does Legal accept the MIT licence on the software as insufficient for the holiday data? Is there a licence statement from the publisher?
6. Does the Copernicus licence allow commercial production use alongside CC BY 4.0?
7. Why does the sales table hold about 310,000 rows when about 64 products over about 4.8 years would be far fewer? Is the count correct, or does it include duplicate or per-transaction rows?
8. Were the 2024-02-05 to 2024-03-10 days closed, or was the till offline? The answer changes whether those days are missing or zero.
9. Does the shop calendar cover every day? The catalog shows about 1,500 rows against about 1,750 calendar days.
10. Is the owner content to use only national holidays, with no local feast days?

---

## Human review gate

Draft generated by the discovery agents for UC2 on 2026-11-10T09:28:50Z (model claude-haiku-5-5). It is a draft for review, not a decision.

Before any profiling or pipeline work, the reviewer confirms:

- [ ] Each verdict is supported by the evidence cited
- [ ] Every licence was read at its source, and the attribution text is recorded
- [ ] Access requests for the feasible-with-conditions sources are raised with the named owners
- [ ] Consent and purpose limits are understood, and the target population is filtered accordingly

**Blocker flags on sources not rejected (resolve or justify):**

- api.nager_public_holidays: LIC-UNKNOWN

**Open questions:**

1. Does Retail Operations hold a pre/post-2024 product code mapping outside the catalogued sources? The wiki says none exists. If it does, who owns it?
2. Is N2 a gate for the whole use case, or can the owner accept a reduced scope (e.g. only products whose codes did not change, or only post-2024-04-01 history)?
3. Which city or coordinates represent the shop for weather queries? No source names it. Is a grid-point proxy acceptable?
4. Who is the accountable owner for the public holiday feed? Is Legal's sign-off enough to act as steward?
5. Does Legal accept that the MIT licence (software repo) does not cover the holiday data? Is there a licence statement from the publisher?
6. Does the Copernicus C3S licence allow commercial production use alongside CC BY 4.0?
7. Why does the sales table hold about 310,000 rows when about 64 products over about 4.8 years would be far fewer? Is the count correct, or does it include duplicate or per-transaction rows?
8. Were the shop closed from 2024-02-05 to 2024-03-10, or was the till offline? This decides whether those days are missing or zero.
9. Does the shop calendar cover every day? The catalog shows about 1,500 rows against about 1,750 calendar days.
10. Is the owner content to use only national holidays, with no local feast days?

Reviewer: ____________________   Date: __________   Decision: proceed / proceed with conditions / stop
