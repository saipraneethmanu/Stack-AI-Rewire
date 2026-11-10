"""Licence and structured-metadata extraction from dataset landing pages."""
from __future__ import annotations

import html as html_lib
import json
import re


def jsonld_datasets(html: str) -> list[dict]:
    """Return every schema.org Dataset object embedded as JSON-LD in a page.

    Many portals (Kaggle, Zenodo, data.gov, Hugging Face, Dataverse, CKAN sites) embed one.
    It is the most reliable machine-readable description of a dataset when it exists.
    """
    found = []
    for m in re.finditer(r"""(?is)<script[^>]*type=["']application/ld\+json["'][^>]*>(.*?)</script>""", html):
        try:
            data = json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else []
        for item in items:
            if isinstance(item, dict) and "Dataset" in str(item.get("@type", "")):
                found.append(item)
    return found


def summarise_jsonld_dataset(d: dict) -> dict:
    """Keep the fields that matter for discovery, clipped for the model."""
    def name_of(v):
        if isinstance(v, list):
            return [name_of(x) for x in v][:5]
        if isinstance(v, dict):
            return v.get("name") or v.get("url") or v.get("@id")
        return v

    def clip(v, n=600):
        v = re.sub(r"<[^>]+>", " ", str(v)) if v is not None else None
        return None if v is None else (" ".join(v.split())[:n])

    dist = d.get("distribution") or []
    dist = dist if isinstance(dist, list) else [dist]
    return {
        "name": d.get("name"), "description": clip(d.get("description")),
        "license": d.get("license"), "creator": name_of(d.get("creator")), "publisher": name_of(d.get("publisher")),
        "datePublished": d.get("datePublished"), "dateModified": d.get("dateModified"),
        "temporalCoverage": d.get("temporalCoverage"), "spatialCoverage": name_of(d.get("spatialCoverage")),
        "isAccessibleForFree": d.get("isAccessibleForFree"), "keywords": clip(d.get("keywords"), 300),
        "variableMeasured": name_of(d.get("variableMeasured")),
        "distribution": [{k: x.get(k) for k in ("contentUrl", "encodingFormat", "fileFormat", "contentSize", "requiresSubscription", "name")
                          if isinstance(x, dict) and x.get(k) is not None} for x in dist[:10]],
    }


# ---------------------------------------------------------------------------
# G1: find the licence of ANY dataset from its landing page
# ---------------------------------------------------------------------------
# Order of evidence: schema.org JSON-LD "license" first, then links to licence pages, then licence
# sentences in the visible text. A licence is only named when a pattern recognises it. "Unknown" and
# "unspecified" are treated as no licence, but the JSON-LD value is kept as the snippet, so the
# record shows what the page actually said.

_SNIPPET_MAX = 400

# CC licence URLs: creativecommons.org/licenses/by-nc-sa/4.0/...
_CC_URL = re.compile(r"creativecommons\.org/licenses/((?:by)(?:-(?:nc|sa|nd))*)/(\d\.\d)", re.I)
# CC names: "CC BY-NC-SA 4.0", "CC-BY 4.0", "cc by-nc 4.0"
_CC_NAME = re.compile(r"\bCC[ -]?(BY((?:[ -](?:NC|SA|ND))*))[ -]?(\d\.\d)\b", re.I)
# Long CC names: "Creative Commons Attribution-NonCommercial 4.0"
_CC_LONG = re.compile(
    r"Creative Commons\s+Attribution((?:-(?:NonCommercial|ShareAlike|NoDerivatives))*)\s+(\d\.\d)", re.I)
_LONG_TO_CODE = {"noncommercial": "NC", "sharealike": "SA", "noderivatives": "ND"}
_CC0 = re.compile(r"creativecommons\.org/publicdomain/zero/1\.0|choosealicense\.com/licenses/cc0|\bCC0(?:[ -]?1\.0)?\b", re.I)
_ODBL = re.compile(r"opendatacommons\.org/licenses/odbl|^\s*ODbL(?:\s*1\.0)?\s*$", re.I)
_OGL = re.compile(r"nationalarchives\.gov\.uk/doc/open-government-licen[cs]e|Open Government Licen[cs]e", re.I)
_OGL_VERSION = re.compile(r"version/(\d)|\bv\.?\s?(\d)(?:\.(\d))?", re.I)
_MIT = re.compile(r"choosealicense\.com/licenses/mit\b|^\s*MIT(?: License)?\s*$", re.I)
_APACHE = re.compile(r"choosealicense\.com/licenses/apache-2\.0|^\s*Apache[- ]2\.0(?: License)?\s*$", re.I)

# Sentences in visible text that name a licence. Matched text is passed to normalise_licence().
_LICENCE_SENTENCE = re.compile(
    r"Creative Commons\s+Attribution[^.;()]{0,60}?\d\.\d"
    r"|\bCC[ -]?BY(?:[ -](?:NC|SA|ND))*[ -]?\d\.\d\b"
    r"|\bCC0(?:[ -]?1\.0)?\b"
    r"|Open Government Licen[cs]e(?:\s+v\.?\s?\d(?:\.\d)?)?"
    r"|\bODbL(?:\s*1\.0)?\b",
    re.I,
)
_ANCHOR = re.compile(r"""(?is)<a\s[^>]*?href=["']([^"']+)["'][^>]*>(.*?)</a>""")
_LICENCE_URL_ANYWHERE = re.compile(
    r"""https?://[^\s"'<>]*(?:creativecommons\.org/licenses/|creativecommons\.org/publicdomain/zero/|"""
    r"""opendatacommons\.org/licenses/|nationalarchives\.gov\.uk/doc/open-government-licen[cs]e)[^\s"'<>]*""",
    re.I,
)


def normalise_licence(text: str | None) -> str | None:
    """Map a licence name or URL to its short canonical name, or None when it is not a known licence."""
    if not text:
        return None
    t = html_lib.unescape(str(text)).strip()

    m = _CC_URL.search(t)
    if m:
        return f"CC {m.group(1).upper()} {m.group(2)}"
    if _CC0.search(t):
        return "CC0 1.0"
    if _ODBL.search(t):
        return "ODbL 1.0"
    if _OGL.search(t):
        v = _OGL_VERSION.search(t)
        if v:
            major = v.group(1) or v.group(2)
            minor = v.group(3) or "0"
            return f"OGL v{major}.{minor}"
        return "OGL"
    if _MIT.search(t):
        return "MIT"
    if _APACHE.search(t):
        return "Apache-2.0"
    m = _CC_NAME.search(t)
    if m:
        return f"CC {m.group(1).upper().replace(' ', '-')} {m.group(3)}"
    m = _CC_LONG.search(t)
    if m:
        codes = [_LONG_TO_CODE[part.lower()] for part in re.findall(r"-(NonCommercial|ShareAlike|NoDerivatives)", m.group(1), re.I)]
        return "CC " + "-".join(["BY", *codes]) + f" {m.group(2)}"
    return None


def _clip(text: str) -> str:
    return " ".join(text.split())[:_SNIPPET_MAX]


def _found(name, url, snippet, found_in) -> dict:
    return {"licence_name": name, "licence_url": url, "snippet": _clip(snippet) if snippet else None, "found_in": found_in}


def _plain_text(html: str) -> str:
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(html_lib.unescape(text).split())


def extract_licence(html: str, jsonld: list[dict] | None = None) -> dict:
    """Return the licence a landing page declares, with the evidence it came from.

    The result always has exactly the keys licence_name, licence_url, snippet and found_in.
    A value that cannot be recognised is returned as None, never guessed.
    """
    if jsonld is None:
        jsonld = jsonld_datasets(html)

    # 1. schema.org JSON-LD. If the value is recognised, stop. If it says "Unknown", keep it as the
    #    evidence (found_in json-ld, name None) and still look at the page for a clearer statement.
    unknown_evidence = None
    for dataset in jsonld:
        value = dataset.get("license")
        if isinstance(value, list):
            value = value[0] if value else None
        if value is None or value == "":
            continue
        if isinstance(value, dict):
            name, url = str(value.get("name") or ""), str(value.get("url") or "")
        else:
            text = str(value)
            name, url = ("", text) if text.startswith("http") else (text, "")
        licence = normalise_licence(name) or normalise_licence(url)
        shown = name or url
        if licence:
            return _found(licence, url or None, shown, "json-ld")
        if unknown_evidence is None:
            unknown_evidence = _found(None, url or None, shown, "json-ld")

    # 2. Links to a licence page (creativecommons.org, opendatacommons.org, nationalarchives.gov.uk ...)
    for href, anchor_html in _ANCHOR.findall(html):
        licence = normalise_licence(href)
        if licence:
            anchor_text = _plain_text(anchor_html) or href
            return _found(licence, href, anchor_text, "link")

    # 3. Licence sentences in the visible text.
    plain = _plain_text(html)
    for match in _LICENCE_SENTENCE.finditer(plain):
        licence = normalise_licence(match.group(0))
        if licence:
            start = max(0, match.start() - 80)
            return _found(licence, None, plain[start:match.end() + 120], "text")

    # 4. Markup. Portals such as OpenDataSoft keep their metadata as HTML-escaped JSON inside element attributes
    #    (for example &quot;license&quot;: &quot;CC BY 4.0&quot;). Tag stripping removes those attributes, so search
    #    the unescaped markup for licence URLs and licence statements as well.
    markup = html_lib.unescape(html)
    for url in _LICENCE_URL_ANYWHERE.findall(markup):
        licence = normalise_licence(url)
        if licence:
            return _found(licence, url, url, "text")
    for match in _LICENCE_SENTENCE.finditer(markup):
        licence = normalise_licence(match.group(0))
        if licence:
            start = max(0, match.start() - 80)
            window = _plain_text(markup[start:match.end() + 120])
            return _found(licence, None, window, "text")

    # Nothing recognised: report the JSON-LD "Unknown" evidence if there was any, otherwise all None.
    if unknown_evidence is not None:
        return unknown_evidence
    return {"licence_name": None, "licence_url": None, "snippet": None, "found_in": None}
