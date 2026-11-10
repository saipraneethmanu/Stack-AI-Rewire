"""Deterministic red-flag rules, run on every catalog record before the Risk Assessor agent.

Why rules and an agent? Rules are cheap, repeatable and testable, and they catch what can be
read from structured fields. The agent adds judgement flags (conflicts, consent gaps,
representativeness, ...) and may dismiss a rule flag only with a written reason, and the
orchestrator enforces that.

Each rule: (record, candidate, use_case, settings) -> list of {"code", "evidence"}.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

Flag = dict

GRAIN_ORDER = ["minute", "15min", "30min", "hourly", "daily", "weekly", "monthly", "quarterly", "annual"]
INACTIVE_STATUSES = {"deprecated", "archived", "frozen", "retired", "decommissioned", "superseded"}


def _flag(code: str, evidence: str) -> Flag:
    return {"code": code, "evidence": evidence}


def _d(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Provided rules (read these as worked examples)
# ---------------------------------------------------------------------------
def rule_licence(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    if record["kind"] == "internal":
        return []
    lic = record.get("licence") or {}
    name = (lic.get("name") or "").strip()
    flags = []
    if not name or name.lower() in {"unknown", "none", "null", "not found", "n/a"}:
        flags.append(_flag("LIC-UNKNOWN", f"No licence established. Evidence field: {lic.get('evidence')!r}"))
    elif re.search(r"\bNC\b|non[- ]?commercial", name, re.I):
        flags.append(_flag("LIC-NONCOMMERCIAL", f"Licence {name!r} restricts commercial use"))
    elif re.search(r"\bBY\b|attribution|OGL|open government", name, re.I):
        flags.append(_flag("LIC-ATTRIBUTION", f"Licence {name!r} requires attribution"))
    if lic.get("mixed_sources"):
        flags.append(_flag("LIC-MIXED", "Record states that parts come from upstream providers with different terms"))
    return flags


def rule_agreement(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    status = ((record.get("licence") or {}).get("agreement_status") or "").lower()
    if record["kind"] == "vendor_feed" and status not in {"active", "signed"}:
        return [_flag("LIC-AGREEMENT-NOT-ACTIVE", f"Vendor feed with agreement_status={status or 'unknown'!r}")]
    return []


def rule_access(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    acc = record.get("access") or {}
    flags = []
    if acc.get("auth_required") or (acc.get("classification") or "").lower() == "restricted":
        flags.append(_flag("ACC-RESTRICTED", f"auth_required={acc.get('auth_required')}, "
                                             f"classification={acc.get('classification')}, process={acc.get('request_process')!r}"))
    if (acc.get("method") or "").lower() in {"manual_export", "manual", "spreadsheet", "email"}:
        flags.append(_flag("ACC-MANUAL", f"Access method {acc.get('method')!r}"))
    if acc.get("reachable") is False:
        flags.append(_flag("ACC-UNREACHABLE", "Record states the source could not be reached or restored"))
    return flags


def rule_payload(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    size = (record.get("access") or {}).get("approx_size_bytes")
    limit = settings["rules"]["large_payload_bytes"]
    if isinstance(size, int) and size > limit:
        return [_flag("OPS-LARGE-PAYLOAD", f"approx_size_bytes={size:,} > {limit:,}")]
    return []


def rule_pii(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    pii_fields = [f["name"] for f in (record.get("schema") or {}).get("fields", []) if f.get("pii") is True]
    declared = (record.get("declared_metadata") or {}).get("contains_pii")
    if pii_fields or declared is True:
        return [_flag("GOV-PII", f"PII fields: {pii_fields or 'declared contains_pii=true'}")]
    return []


def rule_owner(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    if record["kind"] == "internal" and not ((record.get("ownership") or {}).get("owner") or "").strip():
        return [_flag("GOV-OWNER-UNKNOWN", "Internal source with no recorded owner")]
    return []


def rule_status(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    status = (record.get("status") or "").lower()
    if status in INACTIVE_STATUSES:
        return [_flag("GOV-DEPRECATED", f"status={status!r}")]
    return []


# ---------------------------------------------------------------------------
# G4: three deterministic rules. tests/test_learner_gaps.py::test_g4_* checks them.
# ---------------------------------------------------------------------------
def rule_temporal_coverage(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    """Coverage of the candidate's target windows, plus staleness.

    - Skip records whose temporal.grain is "static", or whose start is unknown.
    - Treat a null end as "still updating", i.e. covered up to uc["as_of"].
    - For each window id in candidate["target_windows"], compute the fraction of that window
      (uc["windows"], inclusive dates) covered by [start, end].
        all fractions == 0                                      -> COV-OUT-OF-WINDOW
        otherwise any fraction < settings["rules"]["partial_window_threshold"] -> COV-PARTIAL-WINDOW
    - FRS-STALE if end is not null and end is more than settings["rules"]["stale_after_years"]
      years before uc["as_of"].
    Evidence strings must name the window(s) and the dates you compared.
    """
    temporal = record.get("temporal") or {}
    if temporal.get("grain") == "static":
        return []
    start = _d(temporal.get("start"))
    if start is None:
        return []

    as_of = _d(uc["as_of"])
    end_raw = temporal.get("end")
    end = _d(end_raw) if end_raw else as_of  # open-ended: still updating, covered up to as_of
    thresholds = settings["rules"]
    windows = {w["id"]: w for w in uc["windows"]}

    fractions: dict[str, float] = {}
    for wid in candidate.get("target_windows", []):
        window = windows.get(wid)
        if window is None:
            continue
        w_start, w_end = _d(window["start"]), _d(window["end"])
        window_days = (w_end - w_start).days + 1
        overlap_days = max(0, (min(end, w_end) - max(start, w_start)).days + 1)
        fractions[wid] = overlap_days / window_days

    flags = []
    if fractions:
        detail = ", ".join(f"{wid} {frac:.0%}" for wid, frac in sorted(fractions.items()))
        if all(frac == 0 for frac in fractions.values()):
            flags.append(_flag("COV-OUT-OF-WINDOW",
                               f"Source covers {start}..{end}; no overlap with target windows ({detail})"))
        elif any(frac < thresholds["partial_window_threshold"] for frac in fractions.values()):
            flags.append(_flag("COV-PARTIAL-WINDOW",
                               f"Source covers {start}..{end}; window coverage below "
                               f"{thresholds['partial_window_threshold']:.0%} ({detail})"))

    if end_raw and end < as_of - timedelta(days=round(365.25 * thresholds["stale_after_years"])):
        flags.append(_flag("FRS-STALE",
                           f"Source end {end} is more than {thresholds['stale_after_years']} years before as_of {as_of}"))
    return flags


def rule_grain(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    """COV-GRAIN-MISMATCH if the record's grain is coarser than min_grain of any need the
    candidate serves (candidate["need_ids"] -> uc["needs"]). Only grains in GRAIN_ORDER are
    comparable; "event", "static" and "unknown" on either side never raise the flag."""
    grain = (record.get("temporal") or {}).get("grain")
    if grain not in GRAIN_ORDER:
        return []
    needs = {n["id"]: n for n in uc["needs"]}
    mismatches = []
    for need_id in candidate.get("need_ids", []):
        need = needs.get(need_id)
        if need is None or need.get("min_grain") not in GRAIN_ORDER:
            continue
        if GRAIN_ORDER.index(grain) > GRAIN_ORDER.index(need["min_grain"]):
            mismatches.append(f"{need_id} needs {need['min_grain']} or finer")
    if mismatches:
        return [_flag("COV-GRAIN-MISMATCH", f"Source grain {grain!r} is coarser than: " + "; ".join(mismatches))]
    return []


def rule_metadata_contradiction(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    """DQ-METADATA-CONTRADICTION when record["declared_metadata"]["has_missing_values"] is a
    'no' (False, "no", "false") but documentation_excerpts or quality_notes describe missing
    values (e.g. "missing values", "absence of value", "-200", "?" used as missing, "NaN").
    Careful: "Data set has no missing values" is NOT a contradiction. Strip negated phrases
    before matching."""
    declared = (record.get("declared_metadata") or {}).get("has_missing_values")
    if str(declared).strip().lower() not in {"no", "false"}:
        return []  # the record does not say "no missing values", so there is nothing to contradict
    negated = re.compile(
        r"\b(?:no|without|free of|does not contain|do not contain|not contain|not have|contains no|contain no)"
        r"\s+(?:any\s+)?missing\s+(?:values?|data)\b",
        re.I,
    )
    missing_signal = re.compile(
        r"missing\s+(?:values?|data|entries)|absence of (?:a )?values?|-200\b|\bNaN\b|"
        r"\?\s+(?:is|are|denotes|used|as)\s+(?:a\s+)?missing",
        re.I,
    )
    hits = []
    for text in list(record.get("documentation_excerpts") or []) + list(record.get("quality_notes") or []):
        stripped = negated.sub(" ", str(text))
        match = missing_signal.search(stripped)
        if match:
            hits.append(f"{text!r} (matched {match.group(0)!r})")
    if hits:
        return [_flag("DQ-METADATA-CONTRADICTION",
                      f"Metadata declares has_missing_values={declared!r}, but the documentation says otherwise: "
                      + "; ".join(hits))]
    return []


RULES = [rule_licence, rule_agreement, rule_access, rule_payload, rule_pii, rule_owner, rule_status,
         rule_temporal_coverage, rule_grain, rule_metadata_contradiction]


def evaluate(record: dict, candidate: dict, uc: dict, settings: dict) -> tuple[list[Flag], list[str]]:
    """Run every rule. Returns (flags, warnings). A rule that is not implemented yet is skipped with a warning."""
    flags: list[Flag] = []
    warnings: list[str] = []
    for rule in RULES:
        try:
            for f in rule(record, candidate, uc, settings):
                flags.append({**f, "raised_by": f"rule:{rule.__name__}"})
        except NotImplementedError as exc:
            warnings.append(f"{rule.__name__} skipped: {exc}")
    seen, unique = set(), []
    for f in flags:
        if f["code"] not in seen:
            seen.add(f["code"])
            unique.append(f)
    return unique, warnings
