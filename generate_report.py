"""
Generates a report section grounded strictly in retrieved chunks — Claude is the model
used (this is the "Use Claude first" phase; see docs/use_case_definition.md for the
phase-2 multi-model plan).

The system prompt enforces three hard rules (see docs/methodology.md "Generation"):
  1. Every factual claim must cite a retrieved chunk inline.
  2. Missing data -> write a visible placeholder, never estimate.
  3. Contradictions between sources are surfaced, not silently resolved.
"""

import os

SYSTEM_PROMPT = """You are a real estate research analyst's drafting assistant. You write \
report sections strictly grounded in the source excerpts provided to you. Follow these \
rules with no exceptions:

1. Every factual claim — a number, a date, a named event, a rate, a policy decision — \
must be traceable to one of the provided source excerpts. Cite it inline immediately \
after the claim as (Source: <source_name>, <date>).

2. If part of what you're asked to cover isn't supported by any provided excerpt, write \
exactly: [DATA SOURCE NOT CONNECTED: <brief description of what's missing>] — do NOT \
estimate, infer from general knowledge, or fill the gap with a plausible-sounding number.

3. If two source excerpts disagree or seem inconsistent, state both explicitly and flag \
the discrepancy. Do not silently pick one.

4. Write in the analytical, direct register of institutional real estate research — no \
hedging filler, no marketing language, no invented direct quotes from named individuals.

You will fail this task if you state ANY number or fact that is not present in the \
provided excerpts."""


def build_user_prompt(section_brief: str, retrieved_chunks: list[dict]) -> str:
    sources_block = "\n\n".join(
        f"[EXCERPT {i+1}] Source: {c['source_name']} | Date: {c['date']} | "
        f"URL: {c.get('source_url', 'n/a')}\n{c['text']}"
        for i, c in enumerate(retrieved_chunks)
    )
    return f"""SECTION BRIEF (what to draft):
{section_brief}

PROVIDED SOURCE EXCERPTS (the ONLY facts you may use):
{sources_block}

Draft the section now, following all rules in your system prompt exactly."""


def generate_section(section_brief: str, retrieved_chunks: list[dict],
                      model: str | None = None) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model=model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        max_tokens=1200,
        temperature=0.2,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(section_brief, retrieved_chunks)}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from ingest import load_verified_facts
    from retrieve import LocalVectorStore

    store = LocalVectorStore()
    store.add_chunks(load_verified_facts("verified_facts_2026-08.json"))
    chunks = store.retrieve(
        "central bank policy rate changes since the March 2026 house view", k=5
    )

    brief = (
        "Draft a short 'Rates & Liquidity Update' section (150-250 words) covering what "
        "has changed in ECB, Federal Reserve, and Bank of England policy rates since "
        "March 2026, and what that implies for the report's original financing-cost thesis."
    )
    print(generate_section(brief, chunks))
