"""Extra 9Router / OpenAI-compatible endpoints beyond chat.

These are raw HTTP calls (httpx) because they aren't part of the OpenAI Python
SDK: web search (`/v1/search`) and web fetch (`/v1/web/fetch`).
"""
import httpx

from services.llm_client import get_base_and_key


def _headers(api_key: str) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key and api_key != "no-key":
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def web_search(user, query: str, max_results: int = 5) -> dict:
    base_url, api_key = get_base_and_key(user)
    resp = httpx.post(
        f"{base_url}/search",
        json={"query": query, "max_results": max_results},
        headers=_headers(api_key),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def web_fetch(user, url: str, fmt: str = "markdown", max_chars: int = 0) -> dict:
    base_url, api_key = get_base_and_key(user)
    body = {"url": url, "format": fmt}
    if max_chars:
        body["max_characters"] = max_chars
    resp = httpx.post(
        f"{base_url}/web/fetch",
        json=body,
        headers=_headers(api_key),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()
