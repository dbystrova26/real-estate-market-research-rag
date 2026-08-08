"""
Builds the one fully-worked sample in this repo: a grounded "Rates & Liquidity Update"
covering what's changed since the March 2026 House View, using ONLY the sourced facts in
data/verified_facts_2026-08.json. This is the concrete proof that the grounding pipeline
works end to end — every number below traces to a cited source, and gaps that would need
proprietary data are marked, not filled.

This script's two section bodies were hand-authored (not an LLM call) so the exact same
text used in generate_report.py's live Claude path could be fact-checked deterministically
for this committed example. Running rag/generate_report.py with a real ANTHROPIC_API_KEY
reproduces the same grounded-drafting step live.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest import load_verified_facts
from fact_check import check_draft
from render_report import render_report

SECTION_1_HEADING = "What's Changed Since March 2026"
SECTION_1_BODY = (
    "The report's financing-cost thesis rested on continued central bank easing. The ECB "
    "cut rates eight times from June 2024 to June 2025, then held rates unchanged from "
    "June 2025 until reversing course a year later (Source: UK House of Commons Library, "
    "2026-07-30).\n\n"
    "On 17 June 2026, the ECB raised its deposit facility rate by 25 basis points to 2.25% "
    "(from 2.00%) — its first hike in three years — in response to an energy price shock "
    "tied to the Middle East conflict, which pushed the ECB's 2026 inflation projection to "
    "2.6% (Source: European Central Bank — Monetary policy decision, 2026-06-11). At its "
    "next meeting, the ECB held rates steady, with the deposit facility, main refinancing, "
    "and marginal lending rates unchanged at 2.25%, 2.40%, and 2.65% respectively (Source: "
    "European Central Bank — Economic Bulletin Issue 5, 2026, 2026-07-23).\n\n"
    "The Federal Reserve and Bank of England, whose gradual rate cuts the March report also "
    "cited as supporting improving financing conditions, have both paused rather than "
    "continued cutting. The Fed held its target range at 3.50%-3.75% on 29 July 2026, with "
    "three FOMC members dissenting in favor of a hike, under new Fed Chair Kevin Warsh "
    "(Source: Federal Reserve Board — Implementation Note, 2026-07-29). The Bank of "
    "England's Monetary Policy Committee voted 6-3 to hold Bank Rate at 3.75% at its meeting "
    "ending 29 July 2026, with the three dissenters voting for a hike to 4% (Source: Bank of "
    "England — Monetary Policy Summary and Minutes, July 2026, 2026-07-29)."
)

SECTION_2_HEADING = "Implication for the Report's Financing Thesis"
SECTION_2_BODY = (
    "The March report's central framing — that financing costs would keep falling and debt "
    "would become 'increasingly accretive to property returns' as central banks continued "
    "cutting — no longer holds for the Eurozone specifically: the ECB has reversed into a "
    "hiking stance, and the Fed and Bank of England have paused rather than delivered the "
    "further cuts the report's framing implied.\n\n"
    "[DATA SOURCE NOT CONNECTED: an updated spread between prime office yields and the "
    "EURIBOR curve would be needed to quantify how much of the report's 'accretive debt' "
    "argument has actually eroded — this requires PMA/Bloomberg yield-spread data, which is "
    "not connected in this prototype.]\n\n"
    "[DATA SOURCE NOT CONNECTED: an updated EUR billion figure for European direct real "
    "estate transaction volume in H1 2026 would show whether deal activity slowed in "
    "response to the June hike — this requires MSCI RCA transaction data, which is not "
    "connected in this prototype.]\n\n"
    "What can be said on public information alone: the rate environment this report should "
    "be read against today is one of paused-to-tightening policy, not the continued easing "
    "its financing narrative assumed as recently as March."
)


def main():
    facts = load_verified_facts("data/verified_facts_2026-08.json")
    chunk_dicts = [
        {"text": f.text, "source_name": f.source_name, "source_url": f.source_url, "date": f.date}
        for f in facts
    ]

    sections = []
    for heading, body in [(SECTION_1_HEADING, SECTION_1_BODY), (SECTION_2_HEADING, SECTION_2_BODY)]:
        fc = check_draft(body, chunk_dicts)
        sections.append({"heading": heading, "body": body, "fact_check": fc, "chunks": chunk_dicts})
        print(f"[{heading}] {fc['verdict']} (coverage {fc['coverage_score']:.0%}, "
              f"{fc['placeholders_used']} placeholder(s) used)")

    out_dir = Path("reports/sample")
    out_dir.mkdir(parents=True, exist_ok=True)

    html_path = render_report(
        title="Rates & Liquidity Update",
        subtitle="A RAG-grounded update to the Catella House View, March 2026",
        kicker="Independent research prototype · August 2026 · Not an official Catella publication",
        sections=sections,
        disclaimer=(
            "This is an independent portfolio prototype demonstrating a RAG-grounded "
            "report-drafting pipeline. It is not an official Catella publication, is not "
            "affiliated with or endorsed by Catella AB, and does not reproduce any text, "
            "data, or branding from Catella's copyrighted March 2026 House View. All facts "
            "above are drawn from public central bank sources — see the source list below "
            "and data/verified_facts_2026-08.json for full citations."
        ),
        out_path=str(out_dir / "rates_liquidity_update_2026-08.html"),
    )

    md_lines = [
        "# Rates & Liquidity Update — August 2026",
        "*A RAG-grounded update to the Catella House View, March 2026 — independent prototype, not an official Catella publication.*\n",
    ]
    for sec in sections:
        md_lines.append(f"## {sec['heading']}\n")
        md_lines.append(sec["body"] + "\n")
        md_lines.append(f"*Grounding: {sec['fact_check']['verdict']}*\n")
    (out_dir / "rates_liquidity_update_2026-08.md").write_text("\n".join(md_lines))

    print(f"\nWritten: {html_path}")
    print(f"Written: {out_dir / 'rates_liquidity_update_2026-08.md'}")


if __name__ == "__main__":
    main()
