from __future__ import annotations

import html
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup  # type: ignore


@dataclass
class Tool:
    name: str
    description: str
    json_schema: Dict[str, Any]
    func: Callable[[Dict[str, Any]], str]


def _truncate(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20] + "\n... [truncated]"


def web_search_impl(args: Dict[str, Any]) -> str:
    query: str = str(args.get("query", "")).strip()
    num_results: int = int(args.get("num_results", 5))
    num_results = max(1, min(10, num_results))
    if not query:
        return "No query provided to web_search."

    session = requests.Session()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/117.0 Safari/537.36"
        )
    }
    params = {"q": query}
    resp = session.get("https://duckduckgo.com/html/", params=params, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    results: List[Tuple[str, str]] = []
    for a in soup.select("a.result__a"):
        title = a.get_text(" ", strip=True)
        href = a.get("href", "")
        if not href:
            continue
        results.append((title, href))
        if len(results) >= num_results:
            break

    if not results:
        return f"No results found for query: {query}"

    lines = [f"Top {len(results)} results for: {query}"]
    for idx, (title, href) in enumerate(results, start=1):
        # Unescape any HTML entities and clean whitespace
        lines.append(f"{idx}. {html.unescape(title)}\n   {href}")
    return _truncate("\n".join(lines))


WEB_SEARCH_TOOL = Tool(
    name="web_search",
    description=(
        "Search the web for up-to-date information. Use this when you need current facts, "
        "headlines, or external knowledge. Returns a short list of links and titles."
    ),
    json_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query to look up online",
            },
            "num_results": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "default": 5,
                "description": "How many results to return (1-10)",
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    },
    func=web_search_impl,
)


def get_available_tools() -> List[Tool]:
    if os.getenv("AGENT_DISABLE_TOOLS", "").strip().lower() in {"1", "true", "yes"}:
        return []
    return [WEB_SEARCH_TOOL]


def as_openai_tools_schema(tools: List[Tool]) -> List[Dict[str, Any]]:
    openai_tools: List[Dict[str, Any]] = []
    for t in tools:
        openai_tools.append(
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.json_schema,
                },
            }
        )
    return openai_tools


def execute_tool_call(tools: List[Tool], name: str, arguments_json: str) -> str:
    tool_map: Dict[str, Tool] = {t.name: t for t in tools}
    if name not in tool_map:
        return f"Unknown tool: {name}"
    try:
        args: Dict[str, Any] = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        return "Tool arguments JSON could not be parsed."
    try:
        return tool_map[name].func(args)
    except Exception as exc:  # pragma: no cover
        return f"Tool {name} raised an exception: {exc}"