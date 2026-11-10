# Decisions log

## Source suggestions (Step 2b)
Searches ran through `scripts/web_search.py` with Gemini grounding (see "Step 2b search deviation" below). Each suggestion was checked on its publisher page or metadata endpoint. Raw search output is in `outputs/artifacts/search/`.

| Suggestion (publisher, URL) | Need, window | Decision | Reason |
|---|---|---|---|
| Regione Lombardia / ARPA, Dati sensori aria, `https://www.dati.lombardia.it/Ambiente/Dati-sensori-aria/nicp-bhqi` | N1, prototype and production | Reject | Metadata says CC0 1.0. The data endpoint, sorted ascending, starts at 2026-01-01 and includes -9999 sentinel values. It does not reach 2004–2005 or 2024–2025. |
| Regione Lombardia, Dati sensori meteo, `https://www.dati.lombardia.it/Ambiente/Dati-sensori-meteo/647i-nhxk` | N3, production | Reject | The page says the data are "dati rilevati da sensori in campo nel mese in corso", current month only. No production window. |
| Comune di Bologna, Rilevazione flusso veicoli tramite spire anno 2024, `https://opendata.comune.bologna.it/explore/dataset/rilevazione-flusso-veicoli-tramite-spire-anno-2024/` | N2, production (revised from N2 production as found) | Revise and accept | Page states CC BY 4.0 and hourly counts per loop counter. Covers 2024 only and is a different city from Valdena. Accepted only to test the traffic path. Not client traffic. |
| EUMETSAT training doc, `https://dust.trainhub.eumetsat.int/docs/eea_air_quality.html` | N1 | Reject | Training documentation about EEA air quality, not a dataset with a download. |
| Nager.Date holidays via GitHub listing (`github.com/opendatasicilia/comuni-italiani`) | N4 | Reject | Duplicates `api.nager_public_holidays` from the register. The municipal list is not Valdena's city. |

Inspected through the workflow (accepted extra source): `link.bologna_rilevazione_flusso_veico_a104f7` was inspected with `tool inspect_dataset_link`, profiled, and assessed in UC1. Its licence failure led to the G7 fix below.

Also inspected through the workflow: `link.uci_360` (accepted prescribed link) and `link.europa_sdg_11_52_099aa6`.

### Step 2b search deviation
The gateway returned no citations for `gemini-3.8-flash` or `gemini-3.5-flash-lite` with the README request (`web_search_options: {}` only). Checked on both, and `gpt-5.4-nano` rejected the request. Adding `tools: [{"googleSearch": {}}]` returns `url_citation` annotations. `scripts/web_search.py` sends that tool, keeps `web_search_options`, and resolves each grounding redirect to the publisher URL. The README prompt as written would have produced no citations, so Step 2b would have stopped. Redirects that could not be resolved are printed as UNRESOLVED and must be opened by hand.

## Gate decisions (UC1)
Recorded in `outputs/UC1/gate_decisions.json` (decision and reason written by me).
- `archive.ics.uci.edu/dataset/360`: accept, N1 prototype, NO2 only.
- `ec.europa.eu` Eurostat sdg_11_52 (IT): accept, N6 national context. The host was added to the allowlist (G6) before inspection.
- `catalog.data.gov` Chicago: accept on purpose. Refused with DOMAIN_NOT_ALLOWLISTED; the refusal is the finding. Its host is not on the allowlist.
- `opendata.comune.bologna.it` 2024 spires: accept as a revised N2 production link.

## G1 and G3: one edge case in each function
- **G1, `extract_licence`**: a JSON-LD `license` of `"Unknown"` (Kaggle fixture, dict name "Unknown", empty url). The normaliser returns None for it, but the JSON-LD value is kept as the snippet with `found_in: json-ld`, so the record shows what the page said and does not claim a licence. Without this, the record would silently say "no evidence" for a page that declared a value. A second G1 edge case, found in the real run, is that metadata held in an element attribute as HTML-escaped JSON was invisible to tag stripping. That is the G7 failure below.
- **G3, `jsonstat_summary`**: the Eurostat PM2.5 series lists its time index as 2005, 2007, 2008 … 2023, so 2006 is absent from the index while every listed cell is present. The summary reports `expected_cells` 36 and `missing_cells` 0, which would hide the gap. I added a `TIME_GAPS` warning for consecutive-year gaps. It appears in the summary and in the profiler's view of the series; I did not separately verify how the risk verdict weights it. Missing cells are never treated as zero: list-form and dict-form values are both counted as present only when non-null.

## G4–G5: feasible for one need or window, not another
- **Source and rule:** Eurostat sdg_11_52 (`link.europa_sdg_11_52_099aa6`), `rule_temporal_coverage`.
- **Feasible for (need, window):** N6, none of the windows as a production-ready series. Coverage of the prototype is about 24% of the window (2005 only), which is below the 95% threshold, so it is partial and not usable as a full year. It is context only.
- **Not feasible for (need, window):** N6 production (2024–2025): 0% covered, the series ends in 2023. N6 prototype: partial, below half the window, so not feasible under calibration rule 4.
- **Reason for each dismissed flag:** FRS-STALE on `link.uci_360` is dismissed as "target window is historical and fully covered" (rule 6). The UCI window ends in 2005 and is fully covered. It is kept as a condition only if the production window is taken from the same file, which it is not.

### G5 calibration rationale
Eleven rules under the heading "Verdict calibration rules" in `discovery_agent/prompts/risk_assessor.md`. They map flag patterns to verdicts (blocker → not feasible unless a named person can clear it; major → one condition per window; minor → no verdict change alone), use the severities in `config/red_flags.json`, and treat must needs and could needs differently (rule 10). Rule 6 is the historical-window case that keeps the UCI verdict usable.

### G5 before and after
The rules were already present in the first UC1 run, so I did not measure a calibration-free baseline. The before and after below measure run-to-run variance of the Risk Assessor, not an effect of the rules.
- Before (first full run): UCI feasible with conditions; Eurostat not feasible; Bologna not feasible (LIC-UNKNOWN, COV-PARTIAL-WINDOW, COV-GEO-MISMATCH); Open-Meteo feasible with conditions (LIC-NONCOMMERCIAL, LIC-MIXED, GOV-CATALOG-WIKI-CONFLICT).
- After the G7 fix and assess re-run: UCI feasible with conditions (FRS-STALE added); Eurostat not feasible; Bologna not feasible (LIC-UNKNOWN removed, LIC-ATTRIBUTION and FRS-METADATA-DATE-MISLEADING added); Open-Meteo feasible with conditions (COV-GEO-MISMATCH and LIC-ATTRIBUTION added).
- Overall UC1 verdict and need coverage were unchanged across both runs.

## G6: Allowlist changes
| Host added | Needed for (source, page) | Why nothing broader | Date |
|---|---|---|---|
| `ec.europa.eu` | Eurostat JSON-stat API for sdg_11_52 (link.europa_sdg_11_52). Its copyright notice (licence CC BY 4.0) is on the same host. | The JSON-stat endpoint and the terms page are both on this host. No other Eurostat host is needed. | 2026-11-10 |
| `opendata.comune.bologna.it` | Bologna 2024 spires landing page and its licence metadata (revised N2 link). | The landing page and metadata share this host. The licence URL points to creativecommons.org, which the pipeline does not need to fetch (licence is read from the page). | 2026-11-10 |

Hosts I chose **not** to add:
- `catalog.data.gov` (Chicago distractor): refused by design. Its refusal is the finding recorded in the UC1 run.
- `www.dati.lombardia.it` (Lombardy air and meteo): both suggestions were rejected on their metadata, so no host was needed.
- `creativecommons.org`: the licence is read from landing pages, so the pipeline never fetches it.
- `ec.europa.eu` parent domain (`europa.eu`), `eu`, or any wildcard: not needed.

Latitude and longitude change (the one allowed exception): `api.open_meteo_archive` `default_query` changed from 38.72, -9.14 (Lisbon, the register default) to 45.46, 9.19 (Milan). Reason: the brief places the client in northern Italy, and Valdena is fictional, so no source names its city. Milan is my placeholder for a northern-Italy city; I chose it because it is in Lombardy, where the search turned up city-level open data, though those datasets were rejected on coverage. The memo and review treat this as a placeholder, not the clinic's station area.

## G7: One agent failure, fixed at its cause
- **Symptom:** the Bologna 2024 spires link was recorded as `LIC-UNKNOWN`, a blocker, with the evidence "the page shows no licence statement". The page states CC BY 4.0 in its own metadata, which I checked directly.
- **Evidence:** `outputs/artifacts/g7/before/inspect_bologna.json` (licence null, found_in null) and `outputs/artifacts/g7/before/record_bologna.json` (licence name null, evidence says the claim "could not be verified in any tool output"). The page holds `&quot;license&quot;: &quot;CC BY 4.0&quot;` and `license_url` inside an element attribute.
- **Root cause:** tool. `extract_licence` in `discovery_agent/tools/licence.py` looked for JSON-LD, then links, then sentences in the visible text. The visible text was built by stripping tags first. An HTML attribute holding escaped JSON was removed with its tag, so the licence never reached any of the three passes.
- **Fix:** `discovery_agent/tools/licence.py`. Added step 4: unescape the whole markup, search it for licence URLs (`_LICENCE_URL_ANYWHERE`) and licence statements (`_LICENCE_SENTENCE`), and report the match with `found_in: text`. Tag stripping is applied only to the snippet. JSON-LD, link and visible-text passes are unchanged, so the 9 G1 tests still pass.
- **Re-run:** `python -m discovery_agent tool inspect_dataset_link '{"url": "https://opendata.comune.bologna.it/explore/dataset/rilevazione-flusso-veicoli-tramite-spire-anno-2024/"}' --use-case UC1`, then `run --use-case UC1 --from-stage profile --stop-after profile --only link.bologna_rilevazione_flusso_veico_a104f7 --links-file outputs/UC1/links.json --no-input`, then `run --use-case UC1 --from-stage assess --links-file outputs/UC1/links.json --no-input`.
- **Before / after (measured):**
  - Licence from inspection: null → `CC BY 4.0`, licence_url `https://creativecommons.org/licenses/by/4.0/`, found_in `text`.
  - Record flag: `LIC-UNKNOWN` (blocker) → `LIC-ATTRIBUTION` (minor).
  - Verdict: `not_feasible` before and after. The remaining blockers are coverage (`COV-PARTIAL-WINDOW`, 2024 only) and geography (`COV-GEO-MISMATCH`, different city). The licence is no longer the reason.
  - Model calls and tokens for the re-runs are in `outputs/UC1/run_history.jsonl` (one line per stage run); I did not reconcile them against the first run beyond that.
- **Decision this failure could affect:** whether the Bologna link could be used for N2 at all. Before the fix, the memo would have told Legal that the licence was unknown, which would have blocked a use that the page licence allows. After the fix, the licence question is closed and the blockers are coverage and geography, which is the true position.
- **Related source or test checked:** Bologna page directly; the Eurostat copyright notice (which the pipeline also cannot see, see review_UC1 overrule 3); the G1 acceptance tests (`tests/test_learner_gaps.py -k g1`, 9 passed before and after).

## Other decisions
- **Contact details in records.** The Bologna record copied the publisher's generic mailbox (`opendata@comune.bologna.it`) into the steward field. `check UC1` flagged it as an email-like value. I did not loosen the validator. I added a rule to `discovery_agent/prompts/_shared_rules.md`: record the office name, never the mailbox, phone or street address. The Bologna link was re-profiled and assessed; the check now lists only the review and signoff files.
- **Model id whitespace.** The `ANTHROPIC_MODEL` value in my shell had a trailing space, which the SDK sent as the model name and the gateway rejected with HTTP 400. Trimming the value fixed it. The code was not changed. Setting `ANTHROPIC_MODEL` without trailing whitespace is required for any run.
- **Model availability.** The key allows `claude-haiku-5-5` (HTTP 200), `gpt-5.4-nano`, `gemini-3.5-flash-lite`, `gemini-3.8-flash`, `DeepSeek-V4-Flash` and an embedding model. Opus and Sonnet are not allowed on this key, so all agent runs used Haiku 5.5.
- **Chicago refusal.** Recorded as a finding. The link was not retried beyond the one inspection and the one pipeline pass.
- **Dependency choice.** `pyproject.toml` declares no dependencies and `uv.lock` tracks only the project. Runs use `uv run --no-project --with-requirements requirements.txt`, so `requirements.txt` stays the single source of dependencies, as the brief requires.
