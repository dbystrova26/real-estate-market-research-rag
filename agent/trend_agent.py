"""
The trend agent: searches, reads, and judges — new trends vs. updates to old ones.
Grounded the same way as generate_report.py (cite or flag, never invent).
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ingest import ingest_web
from search_backend import search_web

JUDGE_SYSTEM_PROMPT = """You are a real estate research analyst evaluating whether a set \
of web sources represents a genuinely new market trend, or an update to something \
already known. Follow these rules with no exceptions:

1. Base your judgment ONLY on the provided source excerpts. Never use general knowledge \
to fill in what a trend "probably" looks like.

2. Every factual claim in your output must cite a specific excerpt: (Source: <name>, <date>).

3. If the excerpts don't clearly support a verdict, say so explicitly rather than guessing.

4. Be skeptical of marketing language, conference promotions, and vendor puff pieces.

Return ONLY valid JSON in the exact shape requested in the user prompt, no other text."""


def _chunks_from_search(query: str, k: int = 6) -> list[dict]:
    results = search_web(query, k=k)
    chunks: list[dict] = []
    for r in results:
        try:
            page_chunks = ingest_web(r["url"], source_name=r["title"] or r["url"])
            chunks.extend([{"text": c.text, "source_name": c.source_name,
                             "source_url": c.source_url, "date": c.date} for c in page_chunks[:3]])
        except Exception as e:
            print(f"  [skip] failed to read {r['url']}: {e}")
    return chunks


def discover_new_trends(discovery_queries: list[str], known_themes: list[dict],
                         k_per_query: int = 6) -> list[dict]:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    known_summary = "\n".join(f"- {t['summary']}" for t in known_themes)
    findings = []

    for query in discovery_queries:
        print(f"[discover] searching: {query}")
        chunks = _chunks_from_search(query, k=k_per_query)
        if not chunks:
            print(f"  no readable sources found for '{query}'")
            continue

        sources_block = "\n\n".join(
            f"[EXCERPT {i+1}] {c['source_name']} ({c['date']}): {c['text'][:600]}"
            for i, c in enumerate(chunks)
        )
        user_prompt = f"""KNOWN THEMES (already covered — do NOT report these as new):
{known_summary}

SEARCH QUERY: {query}

SOURCE EXCERPTS:
{sources_block}

Is there a genuinely NEW real estate market trend in these excerpts? Respond with ONLY \
this JSON shape:
{{"is_new_trend": true/false, "trend_summary": "<60 words max, or empty string if not new>", \
"citations": ["<Source Name, date>", ...], "confidence": "high"|"medium"|"low"}}"""

        resp = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
            max_tokens=500, temperature=0.1,
            system=JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        try:
            cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
            verdict = json.loads(cleaned)
        except Exception:
            verdict = {"is_new_trend": False, "trend_summary": "", "citations": [], "confidence": "low",
                       "parse_error": text}
        verdict["query"] = query
        verdict["chunks"] = chunks
        findings.append(verdict)

    return findings


def check_known_trend(theme: dict, k: int = 6) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"[check] {theme['id']}: {theme['search_query']}")
    chunks = _chunks_from_search(theme["search_query"], k=k)
    if not chunks:
        return {"theme_id": theme["id"], "verdict": "INSUFFICIENT_EVIDENCE",
                "explanation": "No readable sources found.", "chunks": []}

    sources_block = "\n\n".join(
        f"[EXCERPT {i+1}] {c['source_name']} ({c['date']}): {c['text'][:600]}"
        for i, c in enumerate(chunks)
    )
    user_prompt = f"""ORIGINAL THESIS (paraphrased):
{theme['summary']}

RECENT SOURCE EXCERPTS:
{sources_block}

Does the recent evidence CONFIRM, CONTRADICT, or meaningfully UPDATE the original \
thesis? Respond with ONLY this JSON shape:
{{"verdict": "CONFIRMED"|"CONTRADICTED"|"UPDATED"|"INSUFFICIENT_EVIDENCE", \
"explanation": "<150 words max, cite sources inline as (Source: name, date)>"}}"""

    resp = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        max_tokens=500, temperature=0.1,
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    try:
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        result = json.loads(cleaned)
    except Exception:
        result = {"verdict": "INSUFFICIENT_EVIDENCE", "explanation": f"Judge parse failure: {text}"}
    result["theme_id"] = theme["id"]
    result["chunks"] = chunks
    return result


if __name__ == "__main__":
    themes = json.loads(Path("catella_march2026_trends.json").read_text())["themes"]

    print("=== Checking known themes for updates ===")
    for theme in themes[:1]:
        result = check_known_trend(theme)
        print(json.dumps({k: v for k, v in result.items() if k != "chunks"}, indent=2))

    print("\n=== Discovering new trends ===")
    discovery_queries = [
        "European real estate emerging asset classes 2026",
        "European commercial real estate new investment trend 2026",
    ]
    findings = discover_new_trends(discovery_queries, themes)
    for f in findings:
        print(json.dumps({k: v for k, v in f.items() if k != "chunks"}, indent=2))
