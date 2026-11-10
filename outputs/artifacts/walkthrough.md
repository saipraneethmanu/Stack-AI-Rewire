# Walkthrough

This is my own account of the files in this repository. Each claim names the file it comes from.

## 1. One rule I wrote and why: window coverage (G4)

`discovery_agent/risk_rules.py`, `rule_temporal_coverage`. For each target window, the rule computes the fraction of that window covered by the source's dates, with a null end read as the as-of date. If every fraction is zero it raises COV-OUT-OF-WINDOW (blocker). If any fraction is below 0.95 it raises COV-PARTIAL-WINDOW (major). FRS-STALE is raised when the source ends more than five years before the as-of date.

The threshold of 0.95 comes from `config/settings.json` (`partial_window_threshold`), not from my choice. Why it matters: the Eurostat series covers 2005 only of the prototype window, about 24%, so it is partial, and it covers none of the production window. The rule gives the verdict that the memo relies on. I checked that the UCI file, which covers the whole prototype window, raises FRS-STALE but not COV-PARTIAL-WINDOW, which is the case the rule is meant to separate.

## 2. One claim traced to its record field

`outputs/UC1/signoff.json`, `traced_conclusion`: source `link.uci_360`, field `temporal.end`. The record file `outputs/UC1/records/link.uci_360.json` has `temporal.end` = `2005-04-04`. The conclusion is that the prototype window is covered in full, which the coverage rule depends on. What could change it is the dataset notes' end date of February 2005, which would cut the prototype coverage below 95%. The notes are in the record's documentation excerpts.

## 3. One rejected source and why

Lombardy air-quality sensors, `https://www.dati.lombardia.it/Ambiente/Dati-sensori-aria/nicp-bhqi`, rejected at Step 2b. I read its Socrata metadata (`outputs/artifacts/search/n1_pm25.txt` holds the search result) and sampled three rows of its data, sorted ascending. The earliest date returned was 2026-01-01, so the dataset holds the current year only. It also contains -9999 sentinel values. It cannot cover the prototype window (2004–2005) or the production window (2024–2025). The licence is CC0, which would have been fine; coverage is what rejects it.

## 4. One memo conclusion

From `outputs/UC1/feasibility_memo.md`: "UCI #360 covers the whole window for hourly pollutants and for temperature and humidity." I overrule the pollutant part of that wording. The file has NO2(GT) reference readings and no PM2.5 column, so N1 is partially met for the prototype. The override is recorded in `outputs/UC1/signoff.json` and `outputs/artifacts/review_UC1.md`.
