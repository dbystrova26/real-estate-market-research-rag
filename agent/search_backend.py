"""
Pluggable web search. Two backends:
  - DuckDuckGo HTML scrape (default, free, no API key)
  - Tavily (optional, needs TAVILY_API_KEY) — more reliable for production use

Either way, results: [{"title", "url", "snippet"}].
"""

import os
import re

import requests


def search_web(query: str, k: int = 6) -> list[dict]:
    if os.getenv("TAVILY_API_KEY"):
        return _search_tavily(query, k)
    return _search_duckduckgo(query, k)


def _search_tavily(query: str, k: int) -> list[dict]:
    resp = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": os.environ["TAVILY_API_KEY"],
            "query": query,
            "max_results": k,
            "search_depth": "basic",
        },
        timeout=20,
    )
    resp.raise_for_status()
    return [
        {"title": r.get("title", ""), "url": r["url"], "snippet": r.get("content", "")[:300]}
        for r in resp.json().get("results", [])[:k]
    ]


def _search_duckduckgo(query: str, k: int) -> list[dict]:
    """No API key needed. Scrapes DuckDuckGo's HTML-only endpoint. Brittle by nature
    of scraping — switch to Tavily for production reliability."""
    resp = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers={"User-Agent": "Mozilla/5.0 (compatible; research-agent/1.0)"},
        timeout=20,
    )
    resp.raise_for_status()

    results = []
    for block in re.findall(
        r'result__a[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?result__snippet[^>]*>(.*?)</a>',
        resp.text, re.DOTALL,
    )[:k]:
        url, title_html, snippet_html = block
        title = re.sub(r"<[^>]+>", "", title_html).strip()
        snippet = re.sub(r"<[^>]+>", "", snippet_html).strip()
        results.append({"title": title, "url": url, "snippet": snippet})

    return results


if __name__ == "__main__":
    for r in search_web("European data center real estate investment 2026", k=5):
        print(f"- {r['title']}\n  {r['url']}\n  {r['snippet'][:100]}...\n")
