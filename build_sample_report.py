"""
Builds the shorter rates-only sample report — deterministic, no API key needed since
it reuses hand-authored, already-fact-checked text rather than a live Claude call.
For the full 6-section report with charts, use build_trend_report.py instead.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest import load_verified_facts
from fact_check import check_draft
from render_report import render_report

SECTION_1_HEADING = "Rates & Liquidity Outlook"
SECTION_1_BODY = (
    "The ECB cut rates eight times from June 2024 to June 2025, then held rates "
    "unchanged from June 2025 until reversing course a year later (Source: UK House "
    "of Commons Library, 2026-07-30).\n\n"
    "On 17 June 2026, the ECB raised its deposit facility rate by 25 basis points to "
    "2.25% (from 2.00%) — its first hike in three years — in response to an energy "
    "price shock tied to the Middle East conflict, which pushed the ECB's 2026 "
    "inflation projection to 2.6% (Source: European Central Bank — Monetary policy "
    "decision, 2026-06-11). At its next meeting, the ECB held rates steady, with the "
    "deposit facility, main refinancing, and marginal lending rates unchanged at "
    "2.25%, 2.40%, and 2.65% respectively (Source: European Central Bank — Economic "
    "Bulletin Issue 5, 2026, 2026-07-23).\n\n"
    "The Federal Reserve and Bank of England have both paused rather than continued "
    "cutting. The Fed held its target range at 3.50%-3.75% on 29 July 2026, with three "
    "FOMC members dissenting in favor of a hike, under new Fed Chair Kevin Warsh "
    "(Source: Federal Reserve Board — Implementation Note, 2026-07-29). The Bank of "
    "England's Monetary Policy Committee voted 6-3 to hold Bank Rate at 3.75% at its "
    "meeting ending 29 July 2026, with the three dissenters voting for a hike to 4% "
    "(Source: Bank of England — Monetary Policy Summary and Minutes, July 2026, "
    "2026-07-29)."
)


def main():
    facts = load_verified_facts("verified_facts_2026-08.json")
    chunk_dicts = [
        {"text": f.text, "source_name": f.source_name, "source_url": f.source_url, "date": f.date}
        for f in facts
    ]

    fc = check_draft(SECTION_1_BODY, chunk_dicts)
    print(f"[{SECTION_1_HEADING}] {fc['verdict']} (coverage {fc['coverage_score']:.0%})")

    cited_chunks = [c for c in chunk_dicts if c["source_name"] in SECTION_1_BODY]
    sections = [{"heading": SECTION_1_HEADING, "body": SECTION_1_BODY,
                 "fact_check": fc, "chunks": cited_chunks}]

    html_path = render_report(
        title="Rates & Liquidity Update",
        subtitle="A RAG-grounded update — August 2026",
        kicker="Independent research prototype",
        sections=sections,
        disclaimer=(
            "This is an independent portfolio prototype. Not an official publication "
            "of, and not affiliated with or endorsed by, any organization referenced."
        ),
        out_path="rates_liquidity_update_2026-08.html",
    )

    md_lines = [
        "# Rates & Liquidity Update — August 2026",
        "*A RAG-grounded update — independent prototype.*\n",
        f"## {SECTION_1_HEADING}\n",
        SECTION_1_BODY + "\n",
    ]
    Path("rates_liquidity_update_2026-08.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(f"\nWritten: {html_path}")
    print("Written: rates_liquidity_update_2026-08.md")


if __name__ == "__main__":
    main()
