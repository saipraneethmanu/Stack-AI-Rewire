# Memo review: UC1 air quality and traffic

Reviewer: Sai Praneeth. Memo reviewed: `outputs/UC1/feasibility_memo.md`, checked against `outputs/UC1/records/`, `risk_assessment.json`, `rule_flags.json` and `trace.jsonl`.

## Where I agree
- **Overall verdict: feasible with conditions, production not yet feasible.** Agree. Every must-need route to production depends on an access request, a Legal decision or a mapping that does not exist yet.
- **The vendor feed (`vendor.atmosdata_pro`) is not usable.** Agree. Its agreement is expired, its endpoint is unreachable, and the schema is undocumented.
- **N5 (patient-level records) is unmet by policy.** Agree. The clinic data policy allows daily district counts only.
- **`internal.traffic.hourly_counts` has a series break on 2024-03-18 and no counter-to-station mapping.** Agree with the memo. The wiki page `counter_replacement_2024` supports the break.
- **`link.uci_360`: the -200 missing code is documented and must be cleaned.** Agree. The record's quality notes show -200 in every numeric column except Date and Time. I checked this against the page notes.
- **`link.uci_360`: the research-only restriction conflicts with the CC BY 4.0 licence field.** Agree, and this is a good catch. The page notes say "This dataset can be used exclusively for research purposes. Commercial purposes are fully excluded." The memo puts this to Legal before use, which is the right step.

## Where I overrule the pipeline, and why
1. **N1 prototype: met with conditions, overridden to partially met.** The UCI file has reference NO2(GT) only. It has no PM2.5 column and comes from a single road-level device. The N1 need is "NO2 or PM2.5", so the file covers half of the pollutant need at best. Recorded as an override in `signoff.json`.
2. **`link.uci_360`: the profiler missed a sentinel.** The record says C6H6(GT) has `sentinel_counts {}` and `non_missing_share 1.0`, yet its minimum is -200.0 with 366 negative values. The record itself says "almost certainly the same -200 missing code … the profiler did not flag them". I did not fix this, because it is a second sentinel miss in the sample profiler, not the one failure I am using for G7. It is a known limitation of the sample profile; the cleaning condition in the memo still applies to C6H6 by the -200 documentation.
3. **`link.europa_sdg_11_52_099aa6`: the licence is recorded as unknown.** The pipeline read only the JSON-stat response, which carries no licence. The Eurostat copyright notice (`ec.europa.eu/eurostat/web/main/help/copyright-notice`) states CC BY 4.0. Under "unknown stays unknown", the pipeline was right not to infer it. The gap is that the terms page was not probed, and the copyright page is on an allowlisted host. Left as a finding for the pipeline; it does not change the N6 verdict, which rests on coverage.
4. **`api.open_meteo_archive`: `who_can_resolve` is empty.** The conditions name the Client Legal team and Procurement, but the field that records them is empty. Calibration rule 2 requires both. I recorded the owners in the conditions and in this review. The verdict is unchanged.
5. **Open-Meteo coordinates.** The memo says production coordinates are not chosen. The register default was Lisbon (38.72, -9.14). I changed it to 45.46, 9.19 (Milan) as a northern-Italy stand-in, because Valdena is fictional and no source names the city. The memo should treat 45.46, 9.19 as a placeholder, not as the clinic's station area, and the signoff condition on the stations stays open.

## Verdict per dataset link (the gate links)
| Link | Need, window | Verdict in the pipeline | My verdict | Why |
|---|---|---|---|---|
| UCI 360 | N1, prototype | feasible with conditions | feasible with conditions, N1 partial | Covers 2004-03-10 to 2005-04-04 (NO2 only). Licence conflict and -200 cleaning are conditions. |
| Eurostat sdg_11_52 (IT) | N6, prototype and production | not feasible | not feasible | Series ends 2023, 2006 absent (TIME_GAPS), 0% of production and about 24% of prototype covered. |
| Chicago open-air-hour-aggregations | N1, prototype | not feasible (refused) | not feasible | Host catalog.data.gov refused (DOMAIN_NOT_ALLOWLISTED). It is a Chicago dataset, not Valdena. Refusal recorded as a finding. |
| Bologna spires 2024 | N2, production (revised) | not feasible | not feasible | Different city; 2024 only. Licence now read as CC BY 4.0 after the G7 fix. Partial coverage and geography mismatch remain. |

## Gate decision
Accept UCI 360 for N1 (prototype), NO2 only, with the Legal and cleaning conditions. Accept Eurostat for N6 as national context only. Accept Chicago on purpose so the refusal is recorded; do not add its host. Accept the Bologna link as a test of the traffic path, not as client traffic. Production stays blocked until the conditions in `signoff.json` are answered.

## Memo conclusion traced
"Production N2 (traffic): the counts span the window but have a series break on 2024-03-18 and no counter-to-station mapping." Traced to `internal.traffic.hourly_counts` in the catalog and wiki page `counter_replacement_2024` (series break date). Not reviewed on data values: access is restricted and only metadata was read.
