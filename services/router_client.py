"""Extra 9Router / OpenAI-compatible endpoints beyond chat.

These are raw HTTP calls (httpx) because they aren't part of the OpenAI Python
SDK: web search (`/v1/search`) and web fetch (`/v1/web/fetch`).

IMPORTANT: both endpoints REQUIRE a `model` (or `provider`) field naming which
upstream provider to use — omitting it returns 400 "Missing required field:
provider". We try a fallback list of providers so the call succeeds regardless
of which ones the user's 9Router instance has credentials for, and only hard-stop
on real auth errors (401/403).
"""
import os

import httpx

from services.llm_client import get_base_and_key

# Provider ids accepted by 9Router (see skills/9router-web-fetch and
# skills/9router-web-search SKILL.md). Order = preference for fallback.
_FETCH_PROVIDERS = ("jina-reader", "firecrawl", "tavily", "exa")
_SEARCH_PROVIDERS = ("tavily", "exa", "serper", "brave-search", "google-pse", "searxng")


def _headers(api_key: str) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key and api_key != "no-key":
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _provider_list(kind: str) -> list:
    """Explicit override via env (comma-sep), else the sensible default list."""
    env = os.getenv(f"{kind.upper()}_PROVIDER")
    if env:
        return [p.strip() for p in env.split(",") if p.strip()]
    return list(_FETCH_PROVIDERS if kind == "fetch" else _SEARCH_PROVIDERS)


def _post(base_url: str, path: str, api_key: str, body: dict) -> dict:
    resp = httpx.post(
        f"{base_url}{path}",
        json=body,
        headers=_headers(api_key),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def web_search(user, query: str, max_results: int = 5, provider: str = None) -> dict:
    """Search the web. Tries providers in fallback order; raises on total failure."""
    base_url, api_key = get_base_and_key(user)
    providers = [provider] if provider else _provider_list("search")
    last_err = None
    for p in providers:
        try:
            return _post(base_url, "/search", api_key, {"model": p, "query": query, "max_results": max_results})
        except httpx.HTTPStatusError as e:
            last_err = f"{p}: HTTP {e.response.status_code}"
            # auth failures are fatal — no provider will work without a key
            if e.response.status_code in (401, 403):
                break
        except Exception as e:  # network/timeout — try next provider
            last_err = f"{p}: {e}"
    raise RuntimeError(f"web search failed for all providers ({last_err})")


def web_fetch(user, url: str, fmt: str = "markdown", max_chars: int = 0, provider: str = None) -> dict:
    """Fetch a URL → markdown/text/html. Tries providers in fallback order."""
    base_url, api_key = get_base_and_key(user)
    providers = [provider] if provider else _provider_list("fetch")
    last_err = None
    for p in providers:
        body = {"model": p, "url": url, "format": fmt}
        if max_chars:
            body["max_characters"] = max_chars
        try:
            return _post(base_url, "/web/fetch", api_key, body)
        except httpx.HTTPStatusError as e:
            last_err = f"{p}: HTTP {e.response.status_code}"
            if e.response.status_code in (401, 403):
                break
        except Exception as e:
            last_err = f"{p}: {e}"
    raise RuntimeError(f"web fetch failed for all providers ({last_err})")
