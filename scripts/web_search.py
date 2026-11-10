"""Search for public dataset suggestions through the Tiger AI Gateway.

Usage: python scripts/web_search.py "<query>"

Standard library only. Reads ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN from the
environment; WEB_SEARCH_MODEL optionally overrides the default model. The token is
never printed. Results are leads: check every URL on its publisher's page.
"""

import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = "gemini-3.8-flash"


def _require(name):
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"Missing environment variable {name}. Export it in this shell and try again.")
    return value


def _resolve(url):
    """Follow a grounding redirect to the publisher URL it points to. Falls back to the input."""
    for method in ("HEAD", "GET"):
        try:
            request = urllib.request.Request(url, method=method, headers={"User-Agent": "web-search-script"})
            with urllib.request.urlopen(request, timeout=30) as response:
                final = response.geturl()
            if final and not final.startswith("https://vertexaisearch.cloud.google.com/"):
                return final
        except (urllib.error.URLError, ValueError):
            continue
    return url


def _citations(payload):
    """Return (title, url) pairs from url_citation annotations, in order, without duplicates."""
    pairs = []
    seen = set()
    for choice in payload.get("choices", []):
        for note in choice.get("message", {}).get("annotations") or []:
            citation = note.get("url_citation") or {}
            url = citation.get("url")
            if url and url not in seen:
                seen.add(url)
                pairs.append((citation.get("title") or "", url))
    return pairs


def main(argv):
    if len(argv) != 2:
        sys.exit('Usage: python scripts/web_search.py "<query>"')
    base = _require("ANTHROPIC_BASE_URL").rstrip("/")
    token = _require("ANTHROPIC_AUTH_TOKEN")
    model = os.environ.get("WEB_SEARCH_MODEL", "").strip() or DEFAULT_MODEL

    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": argv[1]}],
            "web_search_options": {},
            # Without a search tool the gateway returns no citations at all (checked on
            # gemini-3.8-flash and gemini-3.5-flash-lite), so the grounding tool is required.
            "tools": [{"googleSearch": {}}],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base}/v1/chat/completions",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        sys.exit(f"Search request failed with HTTP {exc.code}. Check the gateway model list for {model}.")
    except urllib.error.URLError as exc:
        sys.exit(f"Search request could not reach the gateway: {exc.reason}")

    try:
        answer = payload["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        sys.exit("The search response had no answer text.")

    print(answer.strip())
    print("\nCitations:")
    citations = _citations(payload)
    if not citations:
        print("(none returned)")
    for title, url in citations:
        resolved = _resolve(url)
        if resolved.startswith("https://vertexaisearch.cloud.google.com/"):
            print(f"{title} | UNRESOLVED redirect, open it yourself: {resolved}")
        else:
            print(f"{title} | {resolved}")


if __name__ == "__main__":
    main(sys.argv)
