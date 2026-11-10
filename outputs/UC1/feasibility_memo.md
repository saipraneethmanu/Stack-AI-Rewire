
# UC1 Air quality and traffic: initial data-feasibility memo

As of 2026-10-15. Client: Valdena Civic Health Office (fictional, northern Italy). Overall discovery verdict: **feasible with conditions.** The prototype can start on the UCI #360 file once its conditions are met. Production is not yet feasible: each production need depends on at least one open access request, a Legal decision, or a mapping that does not yet exist.

## 1. Executive summary

The overall verdict is feasible with conditions. The prototype is closer to ready than production.

Facts that drive the verdict:

1. **Prototype (2004-03-10 to 2005-04-04):** UCI #360 covers the whole window for hourly pollutants and for temperature and humidity (`link.uci_360`). Its -200 missing code is documented, so the cleaning rule is feasible. Its licence conflicts: the licence field says CC BY 4.0, but the notes say research use only. Legal must decide this before any use. It is one road-level device in one city, so it supports method building only.
2. **Production N1 (pollutants):** the city station readings cover 2023-01-01 onward, open-ended (`internal.airq.station_readings`). Access is restricted, and VR-03 may have stopped on 2024-06-30. The wiki says so; the catalog still shows the network as active.
3. **Production N2 (traffic):** the Mobility Office counts (`internal.traffic.hourly_counts`) span the window but have a series break on 2024-03-18. No counter-to-station mapping exists. Access is restricted.
4. **Production N3 (temperature and humidity):** Open-Meteo is the only usable path (`api.open_meteo_archive`). Its free tier is non-commercial. The register says production is approved, but the terms page does not support that. Until Legal decides, production use is not permitted. Full-window coverage is not yet probed. The vendor feed is expired and cannot be used.
5. **N5 (patient records) is unmet by policy.** N6 (national deaths) is unmet on coverage. Both are could-priority, so they do not drive the verdict.

## 2. Need coverage

| Need | Need | Priority | Status | Best source(s) | Gap |
|---|---|---|---|---|---|
| N1 | Hourly air-pollutant concentrations | must | met with conditions | link.uci_360 (prototype); internal.airq.station_readings (production) | Prototype: one road-level device, no PM2.5, sparse reference values, licence conflict. Production: EMU access, station list unconfirmed (VR-03). |
| N2 | Hourly vehicle traffic near stations | must | met with conditions | internal.traffic.hourly_counts | Break on 2024-03-18; no counter-to-station mapping; access not tested. Bologna cannot substitute. |
| N3 | Hourly temperature and humidity | must | met with conditions | api.open_meteo_archive (both windows); link.uci_360 (prototype) | Modelled 10 km grid, not stations. Non-commercial licence. Full-window coverage unconfirmed. Vendor feed not usable. |
| N4 | Daily respiratory visits by district | should | met with conditions | internal.clinic.resp_visits_daily | Access; purpose confirmation; no district-to-station key; case definition and zero-day rule undocumented. |
| N5 | Patient-level visit records | could | unmet | none | Clinic policy allows only daily district counts. |
| N6 | National yearly PM2.5 deaths | could | unmet | link.europa_sdg_11_52_099aa6 | Ends 2023: 0% of production window, about 24% of prototype. Licence unknown. |

## 3. Source assessments

### Feasible with conditions

**api.open_meteo_archive**: Open-Meteo Historical Weather API (reanalysis), a gridded modelled weather product served as JSON. Probed at a Milan-area point; the API snapped it to a grid cell at 138 m elevation. Hourly temperature and humidity returned for 2004-03-10 to 2004-03-12 and 2025-12-29 to 2025-12-31.
- Verdict: feasible with conditions for N3. The production use is blocked until Legal decides.
- Flags: LIC-NONCOMMERCIAL (blocker, rule): "You may only use the free API services for non-commercial purposes." The register lists production as approved, which conflicts with the terms page. LIC-MIXED (major, rule): upstream Copernicus/ECMWF terms apply. COV-PARTIAL-WINDOW (minor): end of prototype and start of production not probed. INT-REPRESENTATIVENESS (minor): modelled grid, not station data. GOV-CATALOG-WIKI-CONFLICT (major): candidate note says the register default is Lisbon (38.72, -9.14); register and probes show 45.46 / 9.19.
- Conditions: Legal decision before any production use, or a paid subscription. Record the Valdena location as a justified assumption. Attribution "Weather data by Open-Meteo.com" and Zippenfenig (2023), doi 10.5281/ZENODO.7970649. Probe full windows. Align UTC.

**internal.airq.station_readings**: City station readings (hourly), Environment Monitoring Unit. Hourly NO2 and PM2.5 by station, keyed to a UTC hour-start timestamp. About 4.2 million rows, from 2023-01-01, refreshed hourly (last refreshed 2026-10-14). No coordinates, traffic or weather fields.
- Verdict: feasible with conditions for N1 production only. Cannot serve the prototype.
- Flags: ACC-RESTRICTED (major, rule): access by request to the EMU. GOV-CATALOG-WIKI-CONFLICT (major): wiki says VR-03 was switched off 2024-06-30; catalog shows the network as active. DQ-SENTINEL-VALUES (minor): missing-value coding undocumented; no sample taken.
- Conditions: access request for 2024-01-01 to 2025-12-31; written station list; treat VR-03 after 2024-06-30 as missing, not zero; missing-value coding and completeness per station; confirm whether 2026 values are provisional (window ends 2025-12-31); a station-to-district or coordinate table is needed for any join.

**internal.clinic.resp_visits_daily**: Respiratory visits (daily, by district), Clinical Analytics. Three columns (visit date, district, visit count), no patient identifiers. About 40,000 rows, from 2022-01-01, daily refresh.
- Verdict: feasible with conditions for N4 (should) only. Not for N5.
- Flags: ACC-RESTRICTED (major, rule). GOV-PURPOSE-LIMITATION (major): wiki clinic_data_policy (Data Protection Office, edited 2025-02-01) says only daily district counts may be used for this purpose; patient postcode and age band must not leave clinic systems. INT-NO-JOIN-KEY (major): district is free text, not a standard code. DQ-UNDOCUMENTED-SCHEMA (minor): no ICD-10 case definition, visit-vs-registration rule or zero-day convention.
- Conditions: written Data Protection Office confirmation for the warning use; access from Clinical Analytics; document case definition and date rule; district code scheme and mapping; small-cell suppression rules before sharing.

**internal.traffic.hourly_counts**: Road traffic counts (hourly), Mobility Office. Per counter: counter ID, local timestamp, vehicles. About 15 million rows, from 2021-01-01, refreshed hourly (last refreshed 2026-10-12). Described as near the monitoring stations.
- Verdict: feasible with conditions for N2 production.
- Flags: ACC-RESTRICTED (major, rule): access not tested. GOV-CATALOG-WIKI-CONFLICT (major): wiki counter_replacement_2024 (edited 2024-04-02) says counters were replaced on 2024-03-18 and counting changed from per-direction to combined; "Do not compare counts across the change without adjusting for it." The catalog has no note, and the schema has no direction field. INT-NO-JOIN-KEY (major): no counter-to-station mapping or distances. DQ-DST-ARTEFACTS (minor): time zone of local timestamps not stated.
- Conditions: access request; counter-to-station mapping and distances; handle the break (about 2.5 months of 2024 are on the old basis); confirm time zone and DST rule before joining to UTC data; confirm no counter changes after 2024-04-02.

### Feasible with conditions (prototype only)

**link.uci_360**: UCI #360 Air Quality. Hourly readings from a metal-oxide multisensor at road level in an unnamed, polluted Italian city, paired with reference analyser values for CO, NMHC, benzene, NOx and NO2, plus temperature and humidity. 9,357 rows, the whole file, covering 2004-03-10 to 2005-04-04 per the data. Static.
- Verdict: feasible with conditions for N1 and N3, prototype window only. The FRS-STALE flag was dismissed: the window is historical and fully covered.
- Flags: DQ-METADATA-CONTRADICTION (major, rule): metadata says no missing values, but the documentation says -200 marks missing. DQ-SENTINEL-VALUES (minor): -200 in numeric columns; NMHC(GT) about 90% missing. LIC-MIXED (major, judgement): CC BY 4.0 in the licence field, but "used exclusively for research purposes. Commercial purposes are fully excluded." LIC-ATTRIBUTION (minor, rule). INT-REPRESENTATIVENESS (major, judgement): one device, one city, one year; sensor columns uncalibrated. No PM2.5.
- Conditions: treat every -200 as missing; Legal decision on the research-only restriction before any use; cite De Vito et al. (2008), DOI 10.24432/C59K5F; limit conclusions to method building; note the notes-vs-data date conflict (February vs 2005-04-04).

### Not feasible

**link.bologna_rilevazione_flusso_veico_a104f7**: Comune di Bologna hourly loop counts, 2024 only, with counter positions. Not feasible for N2. Bologna is a different city from Valdena (COV-GEO-MISMATCH, major, judgement). It covers 2024 only (COV-PARTIAL-WINDOW, major, rule). The schema is free-text only and no data file was sampled (DQ-UNDOCUMENTED-SCHEMA, major). Attribution CC BY 4.0 (minor). It may serve only as a pipeline test, not as client traffic.

**link.data_open_air_chicago_hour_aggre_d4970b**: Candidate data.gov link, described as hourly air data from a US city. Not feasible for N1 prototype. The host returned DOMAIN_NOT_ALLOWLISTED. This is a guardrail finding: contents, period, geography and licence are unverified (ACC-UNREACHABLE and LIC-UNKNOWN, both blocker). The title suggests a US city, which fails the Italy geography (COV-GEO-MISMATCH, major). No workaround was sought.

**link.europa_sdg_11_52_099aa6**: Eurostat SDG 11.52, annual national premature deaths from PM2.5 for Italy, 2005 to 2023. Not feasible for N6. Covers 0% of production and about 24% of prototype (COV-PARTIAL-WINDOW, major, rule). Licence not found; copyright page returned 404 (LIC-UNKNOWN, blocker, rule). Metadata contradiction on a missing 2006 time value (minor, judgement). Could-priority only.

**vendor.atmosdata_pro**: Vendor weather feed for N3 production. Not feasible. The contract ended 2025-12-31 with no signed renewal. The API key was revoked 2026-01-01. Approved purposes are empty (LIC-AGREEMENT-NOT-ACTIVE, blocker; ACC-UNREACHABLE, blocker; LIC-UNKNOWN, blocker). Schema, grain and coverage are undocumented. Not called, per vendor-feed rules. Renewal sits with Procurement, outside this project.

## 4. Red-flag register

| Source | Code | Severity | Evidence | Raised by |
|---|---|---|---|---|
| api.open_meteo_archive | LIC-NONCOMMERCIAL | blocker | Terms: free API non-commercial only; register conflicts | rule |
| link.uci_360 | DQ-METADATA-CONTRADICTION | major | has_missing_values "no" vs -200 documented | rule |
| link.uci_360 | LIC-MIXED | major | CC BY 4.0 field vs research-only notes | judgement |
| link.uci_360 | INT-REPRESENTATIVENESS | major | One device, one city, one year | judgement |
| link.uci_360 | DQ-SENTINEL-VALUES | minor | -200 missing code; NMHC about 90% missing | judgement |
| link.uci_360 | LIC-ATTRIBUTION | minor | Cite De Vito et al. 2008 | rule |
| api.open_meteo_archive | LIC-MIXED | major | Upstream Copernicus/ECMWF terms | rule |
| api.open_meteo_archive | GOV-CATALOG-WIKI-CONFLICT | major | Lisbon note vs 45.46/9.19 probe; location unset | judgement |
| api.open_meteo_archive | COV-PARTIAL-WINDOW | minor | End of prototype, start of production not probed | judgement |
| api.open_meteo_archive | INT-REPRESENTATIVENESS | minor | 10 km modelled grid, not station data | judgement |
| internal.airq.station_readings | ACC-RESTRICTED | major | Auth required; access by request to EMU | rule |
| internal.airq.station_readings | GOV-CATALOG-WIKI-CONFLICT | major | VR-03 off 2024-06-30 per wiki; catalog says active | judgement |
| internal.airq.station_readings | DQ-SENTINEL-VALUES | minor | Missing-value coding undocumented | judgement |
| internal.traffic.hourly_counts | ACC-RESTRICTED | major | Auth required; access not tested | rule |
| internal.traffic.hourly_counts | GOV-CATALOG-WIKI-CONFLICT | major | 2024-03-18 counting change not in catalog | judgement |
| internal.traffic.hourly_counts | INT-NO-JOIN-KEY | major | No counter-to-station mapping | judgement |
| internal.traffic.hourly_counts | DQ-DST-ARTEFACTS | minor | Time zone of local timestamps not stated | judgement |
| internal.clinic.resp_visits_daily | ACC-RESTRICTED | major | Auth required; access by request | rule |
| internal.clinic.resp_visits_daily | GOV-PURPOSE-LIMITATION | major | Policy: daily district counts only | judgement |
| internal.clinic.resp_visits_daily | INT-NO-JOIN-KEY | major | Free-text district; no station mapping | judgement |
| internal.clinic.resp_visits_daily | DQ-UNDOCUMENTED-SCHEMA | minor | No case definition or zero-day rule | judgement |
| link.bologna_rilevazione_flusso_veico_a104f7 | COV-GEO-MISMATCH | major | Bologna, not Valdena | judgement |
| link.bologna_rilevazione_flusso_veico_a104f7 | COV-PARTIAL-WINDOW | major | 2024 only | rule |
| link.bologna_rilevazione_flusso_veico_a104f7 | DQ-UNDOCUMENTED-SCHEMA | major | Free-text schema; no sample | judgement |
| link.bologna_rilevazione_flusso_veico_a104f7 | LIC-ATTRIBUTION | minor | CC BY 4.0 | rule |
| link.data_open_air_chicago_hour_aggre_d4970b | ACC-UNREACHABLE | blocker | DOMAIN_NOT_ALLOWLISTED | rule |
| link.data_open_air_chicago_hour_aggre_d4970b | LIC-UNKNOWN | blocker | No licence obtained | rule |
| link.data_open_air_chicago_hour_aggre_d4970b | COV-GEO-MISMATCH | major | Likely US city | judgement |
| link.data_open_air_chicago_hour_aggre_d4970b | DQ-UNDOCUMENTED-SCHEMA | major | Schema "none" | judgement |
| link.europa_sdg_11_52_099aa6 | COV-PARTIAL-WINDOW | major | Ends 2023; 0% production, about 24% prototype | rule |
| link.europa_sdg_11_52_099aa6 | LIC-UNKNOWN | blocker | No licence; copyright page 404 | rule |
| link.europa_sdg_11_52_099aa6 | DQ-METADATA-CONTRADICTION | minor | TIME_GAPS warning; missing 2006 value | judgement |
| vendor.atmosdata_pro | LIC-AGREEMENT-NOT-ACTIVE | blocker | Contract ended 2025-12-31; not renewed | rule |
| vendor.atmosdata_pro | LIC-UNKNOWN | blocker | No licence text or terms URL | rule |
| vendor.atmosdata_pro | ACC-UNREACHABLE | blocker | API key revoked 2026-01-01 | rule |
| vendor.atmosdata_pro | ACC-RESTRICTED | major | Renewal, new key and Legal sign-off needed | rule |
| vendor.atmosdata_pro | DQ-UNDOCUMENTED-SCHEMA | major | Schema, coverage and station locations unknown | judgement |

## 5. Conditions and owners

| Condition | Source(s) | Who can resolve | Blocking which need |
|---|---|---|---|
| Legal decision on production use under non-commercial terms, or a paid subscription | api.open_meteo_archive | Valdena Legal | N3 production |
| Legal decision on research-only restriction vs CC BY 4.0 | link.uci_360 | Valdena Legal | N1 prototype, N3 prototype |
| Record the Valdena location as an assumption in decisions.md | api.open_meteo_archive | Health Office | N3 (both windows) |
| Confirm full-window hourly temperature and humidity coverage | api.open_meteo_archive | Pipeline team | N3 (both windows) |
| Treat -200 as missing in all numeric columns | link.uci_360 | Pipeline team | N1 prototype |
| Access request for 2024-2025 station extract | internal.airq.station_readings | EMU | N1 production |
| Confirm active station list and VR-03 status after 2024-06-30 | internal.airq.station_readings | EMU; Health Office data owner | N1 production |
| Missing-value coding and completeness by station and pollutant | internal.airq.station_readings | EMU | N1 production |
| Access request | internal.traffic.hourly_counts | Mobility Office | N2 production |
| Counter-to-station mapping and distances | internal.traffic.hourly_counts | Mobility Office; EMU or GIS team | N2 production |
| Handle the 2024-03-18 break; confirm time zone | internal.traffic.hourly_counts | Mobility Office | N2 production |
| Written Data Protection Office confirmation of purpose | internal.clinic.resp_visits_daily | Data Protection Office | N4 |
| Access request | internal.clinic.resp_visits_daily | Clinical Analytics | N4 |
| Case definition, date rule, zero-day convention, district code scheme and mapping | internal.clinic.resp_visits_daily | Clinical Analytics; EMU or GIS team | N4 |
| Align UTC time base across air, traffic and weather | api.open_meteo_archive; internal.airq.station_readings; internal.traffic.hourly_counts | Pipeline team | N1, N2, N3 joins |

## 6. Recommended next steps

1. Raise a Legal request on two points: the Open-Meteo non-commercial terms and the UCI research-only licence conflict. Both gate use.
2. Ask the Health Office to set and justify the Valdena location in decisions.md. The location must be near the monitoring stations. The register default (45.46 / 9.19) and the Lisbon note are both in conflict with the brief and must not be used by default.
3. Raise access requests with the EMU (station extract, station list and VR-03 status), the Mobility Office (2024-2025 counts, counter mapping), and Clinical Analytics (daily district counts). Ask the Data Protection Office to confirm the purpose in writing.
4. Decide whether to keep the Chicago and vendor links as dead ends. Do not seek alternative routes to either.
5. Decide whether N6 (Eurostat) is worth pursuing at all. It is could-priority, ends in 2023, and has no licence.
6. Once Legal clears the prototype, profile UCI #360 first: confirm row count and window, apply the -200 rule, and check per-column completeness. Keep it to method building.
7. Once access is granted for production, profile the station readings for VR-03 gaps and completeness, then the traffic counts around 2024-03-18, then the clinic counts for coverage and zero days.
8. Probe Open-Meteo at the full prototype end and production start only after Legal clears the production use.

## 7. Open questions for the human reviewer

1. Which point in Italy is the Valdena location? The brief asks for a justified choice, and the register probe used 45.46 / 9.19. Which reason should go in decisions.md?
2. Does Legal consider the Valdena Civic Health Office's live clinical warning use to be within the Open-Meteo free non-commercial terms, or should a paid subscription be bought? The discovery verdict is conditional, but the blocker flag is still open.
3. Does Legal accept the UCI #360 research-only restriction for the prototype, given the CC BY 4.0 licence field?
4. Is VR-03 still switched off? Did it stop on 2024-06-30 as the wiki says, and should the catalog be corrected?
5. Did the Mobility Office make any counter changes after 2024-04-02?
6. Has the Data Protection Office accepted the warning model as "this surveillance purpose" for daily district counts?
7. Is N6 still needed, given that the only candidate ends in 2023 and has no licence?
8. Should the Chicago link be dropped from the prototype plan, given that it was unreachable and probably covers a US city?

---

## Human review gate

Draft generated by the discovery agents for UC1 on 2026-11-10T10:52:45Z (model claude-haiku-5-5). It is a draft for review, not a decision.

Before any profiling or pipeline work, the reviewer confirms:

- [ ] Each verdict is supported by the evidence cited
- [ ] Every licence was read at its source, and the attribution text is recorded
- [ ] Access requests for the feasible-with-conditions sources are raised with the named owners
- [ ] Consent and purpose limits are understood, and the target population is filtered accordingly

**Blocker flags on sources not rejected (resolve or justify):**

- api.open_meteo_archive: LIC-NONCOMMERCIAL

**Open questions:**

1. Which point in Italy is the Valdena location? The brief asks for a justified choice; the register probe used 45.46 / 9.19 and the Lisbon note conflicts. Which reason should go in decisions.md?
2. Does Legal consider the Valdena Civic Health Office's live clinical warning use within the Open-Meteo free non-commercial terms, or should a paid subscription be bought? The verdict is conditional, but the LIC-NONCOMMERCIAL blocker is still open.
3. Does Legal accept the UCI #360 research-only restriction for the prototype, given the CC BY 4.0 licence field?
4. Is VR-03 still switched off after 2024-06-30 as the wiki says, and should the catalog be corrected?
5. Did the Mobility Office make any counter changes after 2024-04-02?
6. Has the Data Protection Office accepted the warning model as 'this surveillance purpose' for daily district counts?
7. Is N6 still needed, given that the only candidate ends in 2023 and has no licence?
8. Should the Chicago link be dropped from the prototype plan, given it was unreachable and probably covers a US city?

Reviewer: ____________________   Date: __________   Decision: proceed / proceed with conditions / stop
