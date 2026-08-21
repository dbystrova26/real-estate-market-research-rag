"""
The current, recommended entry point for generating the report.

  - New-trend sections stand alone as findings, not framed as "not in the March 2026
    house view."
  - Rates section presented as a current outlook, not "what's changed since March."
  - "Sources Cited" only lists sources actually cited inline in that section's text.
  - Sections with no real content (only a placeholder) are dropped entirely.
  - No visible grounding jargon in the output — fact_check.py still runs internally.
  - Each section carries 3 paragraphs of analysis: facts, implications, positioning.
  - Every section has a supporting chart built from cited (or clearly labeled, simply
    derived) figures.
  - PDF text justified, page numbers, one Helvetica/Inter family throughout.

Run:
    python build_trend_report.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "charts"))
from ingest import load_verified_facts
from fact_check import check_draft
from render_report import render_report
from render_pdf import render_pdf
from build_charts import build_all_charts

FACTS_PATH = "verified_facts_2026-08.json"

# ---------------------------------------------------------------------------
S0_HEADING = "New Trend: Data Centers"
S0_CHART = "datacenter_vacancy"
S0_BODY = (
    "European data centers have moved from a niche, hyperscaler-only play to a "
    "mainstream institutional allocation. The European Data Centre Association "
    "forecasts EUR 176 billion in cumulative investment between 2026 and 2031, with "
    "future growth increasingly constrained by grid capacity and energy access rather "
    "than by investor appetite or available capital (Source: European Data Centre "
    "Association via Data Center Knowledge, 2026-02-09). Demand is outrunning supply: "
    "European vacancy fell below 10% for the first time in late 2024 and CBRE forecasts "
    "it will reach a record low of 6.5% by the close of 2026 (Source: CBRE — European "
    "Data Centres Outlook 2026, 2026-01-01). Fundraising already reflects this — data "
    "centers captured 31% of global real estate capital raised in the nine months to "
    "September 2025, second only to residential (Source: Colliers Global Investor "
    "Outlook 2026 via Urbanitae, 2025-12-09).\n\n"
    "What this means in practice is that the constraint on this asset class has shifted "
    "from capital to power. A site's investment case now turns less on land cost or "
    "zoning and more on whether it has, or can secure, a grid connection — which "
    "reframes underwriting toward energy infrastructure risk in a way conventional real "
    "estate models are not built to price. It also explains why capacity is "
    "decentralizing away from the traditional FLAP-D hubs (Frankfurt, London, "
    "Amsterdam, Paris, Dublin): secondary markets with available grid capacity are "
    "becoming competitive purely on the basis of power access, independent of their "
    "traditional real estate fundamentals.\n\n"
    "For an investor weighing structural versus tactical positioning, data centers sit "
    "uncomfortably in neither bucket as conventionally defined: the demand driver (AI "
    "compute growth) is structural and multi-year, but execution risk is closer to "
    "infrastructure development than to conventional core real estate. We would treat "
    "this as a theme to track closely rather than act on without direct energy-sector "
    "expertise — the operators best positioned are increasingly the ones capable of "
    "securing or co-investing in power supply, not simply acquiring sites."
)

S1_HEADING = "New Trend: Life Sciences Real Estate"
S1_CHART = "lifesciences_vc"
S1_BODY = (
    "European life sciences real estate is being pulled forward by a funding rebound. "
    "Healthcare and life sciences venture capital volumes reached EUR 13.2 billion in "
    "2025, up 2.8% on 2024 (Source: CBRE — European Life Sciences Ecosystems Sector "
    "Guide 2026, 2026-02-24). That capital is landing on fertile ground: European deep "
    "tech and life sciences spinouts are collectively valued at approximately USD 398 "
    "billion, spanning more than 7,300 companies and 167,000 jobs (Source: CBRE — "
    "European Life Sciences Ecosystems Sector Guide 2026, 2026-02-24) — a large and "
    "growing base of occupiers that will eventually need lab and R&D space beyond what "
    "university and incubator campuses can absorb.\n\n"
    "The real estate implication is specificity of asset, not just sector growth. Life "
    "sciences occupiers need labs with secure water-waste treatment, rapid air "
    "circulation, and vibration-controlled floors to meet Good Manufacturing Practice "
    "standards — requirements a standard office conversion cannot cheaply meet. That "
    "raises the barrier to entry for developers and landlords relative to more generic "
    "asset classes, and it means the winning locations are the ones with existing "
    "clinical and research infrastructure to cluster around, not simply the cheapest "
    "available space.\n\n"
    "This points toward a selective, cluster-driven strategy rather than a broad "
    "sector call: the opportunity concentrates in a small number of established and "
    "emerging European hubs with university and hospital research bases, where "
    "occupier demand for specialized space is durable and lease terms tend to run "
    "longer than in mainstream commercial property. Entering these clusters typically "
    "requires either existing lab-conversion expertise or a development partner who has "
    "it — this is not a sector where a generalist office or industrial platform can "
    "simply redeploy capital without new capability."
)

S2_HEADING = "New Trend: Defense & Rearmament-Driven Industrial Demand"
S2_CHART = "defense_spending_target"
S2_BODY = (
    "Europe's rearmament cycle is a fiscal commitment large enough to reshape real "
    "estate demand on its own. NATO members have committed to raise core defense "
    "spending to 3.5% of GDP by 2035, up from a prior target of 2%, with an additional "
    "1.5% earmarked for broader security investment (Source: Janus Henderson "
    "Investors, citing NATO Summit commitments, 2026-02-04). Germany alone has "
    "committed EUR 500 billion to infrastructure and a further EUR 500 billion to "
    "defense over the next decade. At the EU level, the ReArm Europe Plan aims to "
    "unlock EUR 800 billion in defense investment, with the European Commission "
    "raising up to EUR 150 billion on capital markets through the SAFE instrument "
    "(Source: Markets Group — 2026 European Real Estate Allocator Outlook, "
    "2026-08-01).\n\n"
    "For real estate, the opportunity is mostly indirect rather than direct ownership "
    "of military assets. Defense investment concentrates in urban clusters where "
    "technology talent and research infrastructure intersect — Munich and the "
    "Rhine-Ruhr Valley are cited as primary German beneficiaries, driven by "
    "concentrations of defense-technology companies working on drones, cybersecurity, "
    "and advanced electronics near strong university research bases (Source: Markets "
    "Group — 2026 European Real Estate Allocator Outlook, 2026-08-01). That cluster "
    "formation generates knock-on demand across residential, office, and industrial "
    "and logistics real estate in those specific cities, not a diffuse nationwide "
    "uplift.\n\n"
    "The practical read for positioning is the same discipline required for the data "
    "center theme above: getting the macro trend right is only half the exercise. The "
    "real estate opportunity sits with occupiers and supply chains clustering around "
    "specific technology and manufacturing hubs, which argues for identifying those "
    "hub cities directly — logistics and light-industrial assets near defense-"
    "manufacturing clusters, and residential/office demand in the surrounding labor "
    "markets — rather than a generic 'defense theme' allocation."
)

S3_HEADING = "Rates & Liquidity Outlook"
S3_CHART = "policy_rates"
S3_BODY = (
    "The financing backdrop for European real estate has shifted from easing to a "
    "paused-to-tightening stance. On 17 June 2026, the ECB raised its deposit facility "
    "rate by 25 basis points to 2.25% — its first hike in three years, following eight "
    "consecutive cuts between June 2024 and June 2025 (Source: UK House of Commons "
    "Library, 2026-07-30) — in response to an energy price shock tied to the Middle "
    "East conflict that pushed the ECB's 2026 inflation projection to 2.6% (Source: "
    "European Central Bank — Monetary policy decision, 2026-06-11). The ECB held "
    "steady at its next meeting, with the deposit facility, main refinancing, and "
    "marginal lending rates unchanged at 2.25%, 2.40%, and 2.65% (Source: European "
    "Central Bank — Economic Bulletin Issue 5, 2026, 2026-07-23). The Federal Reserve "
    "and Bank of England have followed the same pattern of pausing rather than "
    "continuing to cut: the Fed held at 3.50%-3.75% on 29 July 2026 with three dissents "
    "favoring a hike, under new Chair Kevin Warsh (Source: Federal Reserve Board — "
    "Implementation Note, 2026-07-29), and the Bank of England's MPC voted 6-3 to hold "
    "at 3.75%, with the three dissenters wanting a hike to 4% (Source: Bank of England "
    "— Monetary Policy Summary and Minutes, July 2026, 2026-07-29).\n\n"
    "The practical implication is that underwriting built on a falling-rate base case "
    "needs revisiting. Debt that looked increasingly accretive to returns under a "
    "continued-cutting assumption is now, at minimum, a flatter picture, and for any "
    "deal underwritten with an exit-cap-rate-compression assumption tied to further "
    "easing, that assumption should be re-tested against a paused-to-tightening base "
    "case. The proximate cause — an energy-driven inflation shock rather than a "
    "demand-side overheating — also matters: this is not necessarily the start of a "
    "new multi-hike cycle, but it is a clear signal that the rate environment is no "
    "longer a one-directional tailwind.\n\n"
    "For positioning, this argues for weighting income durability over cap-rate-"
    "compression-dependent underwriting until the direction of the next one or two "
    "central bank decisions is clearer. Assets with strong, contracted income and "
    "limited near-term refinancing exposure are better placed to absorb a period of "
    "rate uncertainty than assets whose return case depends on financing costs "
    "continuing to fall."
)

S4_HEADING = "Transaction Volumes & Capital Flows"
S4_CHART = "h1_investment_by_sector"
S4_BODY = (
    "The March report cited EUR 225 billion traded in European direct real estate for "
    "full-year 2025 (Source: March 2026 house view, restated here for comparison). The "
    "most current figure shows momentum continuing into 2026: European real estate "
    "investment reached EUR 116 billion in H1 2026 alone, up 10% year-on-year (Source: "
    "CBRE — European Real Estate Investment Figures, H1 2026, 2026-07-30). The "
    "composition of that capital has also shifted from the March report's framing, "
    "which emphasized hotels and offices concentrated in London and Paris. The UK led "
    "H1 investment at EUR 26.5 billion, followed by Germany (EUR 16.2 billion) and Spain "
    "(EUR 12 billion, up 59% year-on-year) — a materially broader geographic spread. "
    "Living accounted for 26% of H1 investment, up 17% year-on-year, and offices drew "
    "EUR 22.6 billion, up 13% year-on-year (Source: CBRE — European Real Estate "
    "Investment Figures, H1 2026, 2026-07-30).\n\n"
    "The office recovery is the more notable shift here. Office was the sector the "
    "March report treated most cautiously, framing it as a 'cherry picking' exercise "
    "limited to supply-constrained, sustainability-certified assets in gateway cities. "
    "A 13% year-on-year increase in office investment volume suggests capital is "
    "returning to the sector faster than that cautious framing anticipated, even as the "
    "financing backdrop has turned less favorable, which points to investors "
    "increasingly pricing in stabilizing occupier fundamentals ahead of, rather than "
    "waiting for, further rate clarity.\n\n"
    "Spain's 59% year-on-year increase and the broader spread of capital beyond the "
    "traditional UK/France/Germany core also reinforce a theme worth tracking "
    "independently: capital is diversifying into markets that offer relative value "
    "after a longer repricing cycle, not only concentrating further into the largest, "
    "most liquid gateway cities."
)

S5_HEADING = "Structural Theme: Affordable Housing Supply Gap"
S5_CHART = "affordable_housing_gap"
S5_BODY = (
    "The affordable-housing shortfall is verifiable directly against a primary policy "
    "source. The European Commission estimates the EU needs to add roughly 650,000 "
    "dwellings per year on top of the 1.6 million currently built annually to close "
    "the supply-demand gap over the next decade, at an estimated cost of EUR 150 "
    "billion per year (Source: European Commission — Affordable Housing Plan, Staff "
    "Working Document SWD 2025-1053-2, 2025-12-16). Looking further out, the "
    "Commission's Joint Research Centre projects a cumulative shortfall of 7.14 "
    "million dwellings by 2035 beyond what's already planned (Source: European "
    "Commission Joint Research Centre, 2025-12-16). The affordability backdrop behind "
    "that demand is stark: EU house prices have risen more than 60% and rents more "
    "than 20% over the past decade, and an estimated 42 million Europeans cannot "
    "afford to adequately heat their homes (Source: European Commission — Housing, "
    "2025-12-16).\n\n"
    "The scale and pan-European consistency of this shortfall is what makes it a "
    "genuinely structural thesis rather than a cyclical one — it is not sensitive to "
    "the rate environment or transaction-volume cycle discussed above the way most "
    "other sectors are. Rental housing, and affordable-rent product specifically, sits "
    "on the right side of a supply-demand imbalance that a single policy plan will not "
    "close quickly: the Commission's own 650,000-unit annual gap is roughly 40% on top "
    "of current build rates, which is not a shortfall construction activity closes "
    "within a normal cycle.\n\n"
    "The remaining work for an analyst here is market selection, not validating "
    "whether the theme itself is real — the direction of the thesis is "
    "well-supported at the pan-European level from public sources alone; identifying "
    "which specific submarkets show the tightest imbalance requires institutional-"
    "grade, market-level data this pipeline does not have access to."
)


def filter_cited_chunks(body: str, chunks: list[dict]) -> list[dict]:
    return [c for c in chunks if c["source_name"] in body]


def build_section(heading: str, body: str, chunk_dicts: list[dict], chart_key: str) -> dict:
    fc = check_draft(body, chunk_dicts)
    print(f"[{heading}] {fc['verdict']} (coverage {fc['coverage_score']:.0%})")
    cited_chunks = filter_cited_chunks(body, chunk_dicts)
    return {"heading": heading, "body": body, "fact_check": fc,
            "chunks": cited_chunks, "chart_path": None, "chart_key": chart_key}


def main():
    charts = build_all_charts()

    facts = load_verified_facts(FACTS_PATH)
    chunk_dicts = [
        {"text": f.text, "source_name": f.source_name, "source_url": f.source_url, "date": f.date}
        for f in facts
    ]
    reference_chunk = {
        "text": "The Catella House View, March 2026, states EUR 225 billion traded "
                "in European direct real estate in 2025, a 5% increase year-on-year.",
        "source_name": "March 2026 house view",
        "source_url": "",
        "date": "2026-03-01",
    }
    all_chunks = chunk_dicts + [reference_chunk]

    sections = [
        build_section(S0_HEADING, S0_BODY, all_chunks, S0_CHART),
        build_section(S1_HEADING, S1_BODY, all_chunks, S1_CHART),
        build_section(S2_HEADING, S2_BODY, all_chunks, S2_CHART),
        build_section(S3_HEADING, S3_BODY, all_chunks, S3_CHART),
        build_section(S4_HEADING, S4_BODY, all_chunks, S4_CHART),
        build_section(S5_HEADING, S5_BODY, all_chunks, S5_CHART),
    ]
    for sec in sections:
        sec["chart_path"] = charts[sec["chart_key"]]

    common_kwargs = dict(
        title="Real Estate Market Research Update",
        subtitle="New trends and a market outlook — August 2026",
        kicker="Independent research prototype",
        sections=sections,
        disclaimer=(
            "This is an independent portfolio prototype. It is not an official "
            "publication of, and is not affiliated with or endorsed by, any "
            "organization referenced within it. This update covers themes verifiable "
            "against current public sources; sections requiring proprietary "
            "institutional data feeds are omitted rather than estimated. All charts "
            "are built from cited figures, with any simple arithmetic derivation "
            "labeled directly on the chart — see methodology.md and "
            "source_registry.md for full sourcing detail."
        ),
    )

    html_path = render_report(out_path="real_estate_market_research_update_2026-08.html", **common_kwargs)
    pdf_path = render_pdf(out_path="real_estate_market_research_update_2026-08.pdf",
                           new_trend_section_ids=[S0_HEADING, S1_HEADING, S2_HEADING], **common_kwargs)

    md_lines = [
        "# Real Estate Market Research Update — August 2026",
        "*New trends and a market outlook — independent prototype.*\n",
    ]
    for sec in sections:
        md_lines.append(f"## {sec['heading']}\n")
        md_lines.append(sec["body"] + "\n")
    Path("real_estate_market_research_update_2026-08.md").write_text(
        "\n".join(md_lines), encoding="utf-8"
    )

    print(f"\nWritten: {html_path}")
    print(f"Written: {pdf_path}")
    print("Written: real_estate_market_research_update_2026-08.md")


if __name__ == "__main__":
    main()
