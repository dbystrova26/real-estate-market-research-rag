"""
Turns a verified finding into a full report section: 3-paragraph analytical prose plus
chart-ready numbers extracted from the same sources — both grounded the same way as
elsewhere in this pipeline. This is what makes the autonomous pipeline
(run_autonomous_report.py) not need a human to hand-write prose for every run.
"""

import json
import os

SECTION_SYSTEM_PROMPT = """You are drafting a section of an institutional real estate \
research report, in the register used by firms like CBRE, Savills, and Cushman & \
Wakefield: direct, analytical, no marketing language, no hedging filler.

Follow these rules with no exceptions:

1. Every factual claim must cite one of the provided source excerpts inline as \
(Source: <source_name>, <date>). Copy source_name EXACTLY as given.

2. Never state a fact not present in the provided excerpts.

3. Write exactly 3 paragraphs:
   - Paragraph 1: the facts, with citations.
   - Paragraph 2: what the facts imply — reasoned analysis, clearly derived from
     paragraph 1's facts, not a new claim.
   - Paragraph 3: the positioning takeaway for an investor.

4. Do not compare this section's topic against any other report unless explicitly asked.

5. Never fabricate a quote from a named individual.

Return ONLY valid JSON: {"heading": "<short section heading, a few words>", \
"body": "<the 3 paragraphs, separated by \\n\\n>"}"""

CHART_DATA_SYSTEM_PROMPT = """You extract chart-ready numeric data points from source \
excerpts for a real estate research report. Follow these rules:

1. Only extract numbers EXPLICITLY stated in the excerpts. Never estimate or infer.

2. A simple, clearly-labeled arithmetic derivation is allowed, flagged with "derived".

3. Extract at most 5 data points.

4. If there aren't at least 2 comparable numeric data points, return an empty list.

Return ONLY valid JSON: {"chart_title": "<short title>", "data_points": \
[{"label": "<short label>", "value": <number>, "unit": "<e.g. '%', 'EUR bn'>", \
"derived": true/false, "note": "<source name + date, or derivation note>"}]}"""


def _client():
    import anthropic
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _chunks_block(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[EXCERPT {i+1}] Source: {c['source_name']} | Date: {c['date']}\n{c['text'][:700]}"
        for i, c in enumerate(chunks)
    )


def write_section(topic_brief: str, chunks: list[dict], model: str | None = None) -> dict:
    client = _client()
    user_prompt = f"""TOPIC BRIEF: {topic_brief}

SOURCE EXCERPTS (the ONLY facts you may use):
{_chunks_block(chunks)}

Draft the section now."""

    resp = client.messages.create(
        model=model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        max_tokens=1200, temperature=0.2,
        system=SECTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    return json.loads(cleaned)


def extract_chart_data(topic_brief: str, chunks: list[dict], model: str | None = None) -> dict | None:
    client = _client()
    user_prompt = f"""TOPIC: {topic_brief}

SOURCE EXCERPTS:
{_chunks_block(chunks)}

Extract chart data now."""

    resp = client.messages.create(
        model=model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        max_tokens=500, temperature=0.1,
        system=CHART_DATA_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    try:
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        result = json.loads(cleaned)
    except Exception:
        return None
    if not result.get("data_points") or len(result["data_points"]) < 2:
        return None
    return result
