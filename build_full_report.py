"""
Builds the FULL house-view-style report: every section a report like this needs,
not just the one rates update. Sections with public sourcing get real, grounded,
cited content. Sections that would require proprietary data (Green Street, MSCI RCA,
PMA, Oxford Economics) are included as real sections with an explicit
[DATA SOURCE NOT CONNECTED] block instead of invented figures — see source_registry.md
for exactly which of the original report's 8 sources are public vs. paid.

This is the single script to run for the complete report:
    python build_full_report.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest import load_verified_facts
from fact_check import check_draft
from render_report import render_report

# ---------------------------------------------------------------------------
# Section 1 — Rates & Liquidity (same grounded content as build_sample_report.py)
# ---------------------------------------------------------------------------
S1_HEADING = "Rates & Liquidity: What's Changed Since March 2026"
S1_BODY = (
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

S2_HEADING = "Implication for the Report's Financing Thesis"
S2_BODY = (
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

# ---------------------------------------------------------------------------
# Section 2 — Structural Theme: Affordable Housing (grounded in EC data)
# ---------------------------------------------------------------------------
S3_HEADING = "Structural Theme: Affordable Housing Supply Gap"
S3_BODY = (
    "The affordable-housing thesis is one of the few structural themes this pipeline can "
    "verify directly against a primary policy source rather than a market-data provider. "
    "The European Commission estimates the EU needs to add roughly 650,000 dwellings per "
    "year on top of the 1.6 million currently built annually to close the supply-demand "
    "gap over the next decade, at an estimated cost of EUR 150 billion per year (Source: "
    "European Commission — Affordable Housing Plan, Staff Working Document SWD "
    "2025-1053-2, 2025-12-16). Looking further out, the Commission's Joint Research Centre "
    "projects that by 2035 more than 2 million new homes per year will be needed EU-wide, "
    "implying a cumulative shortfall of 7.14 million dwellings beyond the 17.06 million "
    "units already planned (Source: European Commission Joint Research Centre, "
    "2025-12-16).\n\n"
    "The affordability backdrop behind that demand is stark: average EU house prices have "
    "risen more than 60% and rents more than 20% over the past decade, and an estimated 42 "
    "million Europeans cannot afford to adequately heat their homes (Source: European "
    "Commission — Housing, 2025-12-16).\n\n"
    "[DATA SOURCE NOT CONNECTED: which specific submarkets show the tightest supply-demand "
    "imbalance, and at what rent levels affordable housing assets are currently underwritten, "
    "would require PMA market-level data, which is not connected in this prototype.]"
)

# ---------------------------------------------------------------------------
# Section 3 — Structural Theme: Operational Living (fully gated — no public source)
# ---------------------------------------------------------------------------
S4_HEADING = "Structural Theme: Operational Living"
S4_BODY = (
    "[DATA SOURCE NOT CONNECTED: this pipeline could not verify claims about operational "
    "living (senior housing, co-living, student housing, serviced apartments) against any "
    "public source. The original report's investment conviction here — including specific "
    "supply-growth figures for senior housing beds by 2050 — is attributed to Green Street "
    "Advisors and the European Commission jointly; the underlying Green Street analysis is "
    "not publicly accessible, so no claim in this section can be independently verified. "
    "Rather than restate the original report's numbers as if re-derived, or invent new ones, "
    "this section is left empty pending a connected data source.]"
)

# ---------------------------------------------------------------------------
# Section 4 — Tactical Opportunities: Retail & Logistics (fully gated)
# ---------------------------------------------------------------------------
S5_HEADING = "Tactical Opportunities: Retail & Logistics"
S5_BODY = (
    "[DATA SOURCE NOT CONNECTED: retail and logistics tactical calls depend on prime yield "
    "and vacancy-rate data (PMA) and transaction-level pricing (MSCI RCA), neither of which "
    "is connected in this prototype. No claim about retail pricing, logistics rental growth, "
    "or specific market recommendations can be verified without those feeds — this section "
    "intentionally ships empty rather than with estimated figures.]"
)

# ---------------------------------------------------------------------------
# Section 5 — Investor Focus: what this pipeline can and can't confirm
# ---------------------------------------------------------------------------
S6_HEADING = "Investor Focus — Grounding Status by Theme"
S6_BODY = (
    "The table below mirrors the structure of a typical house view's 'big calls' grid, but "
    "reports grounding status instead of investment recommendations — this pipeline's job "
    "is to show what can currently be verified, not to originate investment advice.\n\n"
    "Affordable housing: GROUNDED — EU Commission supply-gap and cost figures verified above.\n"
    "Operational living: NOT CONNECTED — requires Green Street/PMA data on senior housing "
    "and flexible-living supply.\n"
    "Retail (parks, grocery, non-discretionary): NOT CONNECTED — requires PMA prime yield "
    "and vacancy data.\n"
    "Logistics & light industrial: NOT CONNECTED — requires PMA rental growth and vacancy "
    "data by corridor.\n"
    "CBD office: NOT CONNECTED — requires PMA/Bloomberg yield-spread data to assess the "
    "'accretive debt' thesis discussed above.\n\n"
    "Of five structural/tactical themes typically covered in a report like this, one is "
    "fully grounded in public sources today; four require institutional data access this "
    "prototype does not have. That ratio is itself the honest headline finding of this "
    "project: public sources cover macro and policy well, but the sector-specific pricing "
    "calls that make a house view distinctive are almost entirely proprietary."
)


def build_section(heading: str, body: str, chunk_dicts: list[dict]) -> dict:
    fc = check_draft(body, chunk_dicts)
    print(f"[{heading}] {fc['verdict']} (coverage {fc['coverage_score']:.0%}, "
          f"{fc['placeholders_used']} placeholder(s) used)")
    return {"heading": heading, "body": body, "fact_check": fc, "chunks": chunk_dicts}


def main():
    facts = load_verified_facts("verified_facts_2026-08.json")
    chunk_dicts = [
        {"text": f.text, "source_name": f.source_name, "source_url": f.source_url, "date": f.date}
        for f in facts
    ]

    sections = [
        build_section(S1_HEADING, S1_BODY, chunk_dicts),
        build_section(S2_HEADING, S2_BODY, chunk_dicts),
        build_section(S3_HEADING, S3_BODY, chunk_dicts),
        build_section(S4_HEADING, S4_BODY, chunk_dicts),
        build_section(S5_HEADING, S5_BODY, chunk_dicts),
        build_section(S6_HEADING, S6_BODY, chunk_dicts),
    ]

    html_path = render_report(
        title="Real Estate Market Research Update",
        subtitle="A RAG-grounded update — August 2026, using a public March 2026 house view as reference case",
        kicker="Independent research prototype · Every claim cited or flagged, never invented",
        sections=sections,
        disclaimer=(
            "This is an independent portfolio prototype demonstrating a RAG-grounded "
            "report-drafting pipeline. It is not an official publication of, and is not "
            "affiliated with or endorsed by, the organization whose report is used as a "
            "reference case. No text, data, or branding from that copyrighted report is "
            "reproduced here. Sections marked [DATA SOURCE NOT CONNECTED] indicate claims "
            "that would require proprietary institutional data feeds this prototype does "
            "not have access to — see source_registry.md for the full breakdown of which "
            "sources are public vs. paid, and why nothing was estimated to fill the gap."
        ),
        out_path="real_estate_market_research_update_2026-08.html",
    )

    md_lines = [
        "# Real Estate Market Research Update — August 2026",
        "*A RAG-grounded update, using a public March 2026 house view as reference case — independent prototype, not an official publication.*\n",
    ]
    for sec in sections:
        md_lines.append(f"## {sec['heading']}\n")
        md_lines.append(sec["body"] + "\n")
        md_lines.append(f"*Grounding: {sec['fact_check']['verdict']}*\n")
    Path("real_estate_market_research_update_2026-08.md").write_text(
        "\n".join(md_lines), encoding="utf-8"
    )

    total_grounded = sum(len(s["fact_check"]["unverified_claims"]) == 0 for s in sections)
    print(f"\n{total_grounded}/{len(sections)} sections fully grounded, "
          f"{len(sections) - total_grounded} contain flagged gaps.")
    print(f"\nWritten: {html_path}")
    print("Written: real_estate_market_research_update_2026-08.md")


if __name__ == "__main__":
    main()
