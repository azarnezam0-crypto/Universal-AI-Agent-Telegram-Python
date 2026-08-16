"""Tool/function definitions the model can call during an agentic chat turn.

Each tool has:
  - a JSON-schema description (TOOL_DEFINITIONS) sent to the model, and
  - a python implementation in TOOL_REGISTRY (name -> callable(user, **args) -> str).

To add a new "skill", just append a definition here + a function — the model
will then be able to use it automatically, no new Telegram command needed.
"""
from services.router_client import web_search, web_fetch


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for up-to-date information, news, or any query. "
                "Returns a list of results with titles, URLs, and snippets."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."},
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results to return (default 5).",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": (
                "Fetch the content of a web page URL and return it as markdown text. "
                "Use to read articles, documentation, or any webpage the user mentions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Full URL to fetch."},
                },
                "required": ["url"],
            },
        },
    },
]


def _web_search(user, query: str, max_results: int = 5) -> str:
    data = web_search(user, query, int(max_results))
    results = data.get("results") or []
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results[:8], 1):
        lines.append(f"{i}. {r.get('title', '')}\n{r.get('url', '')}\n{(r.get('snippet') or '').strip()}")
    return "\n\n".join(lines)


def _web_fetch(user, url: str) -> str:
    data = web_fetch(user, url, "markdown", 8000)
    content = data.get("content") or {}
    text = content.get("text") if isinstance(content, dict) else None
    if not text:
        text = data.get("content") or ""
    if not text:
        return "No content could be extracted from that URL."
    return f"Title: {data.get('title', '')}\n\n{text}"


TOOL_REGISTRY = {
    "web_search": _web_search,
    "web_fetch": _web_fetch,
}
