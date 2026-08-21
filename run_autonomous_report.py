"""
The autonomous pipeline: discovers trends, drafts, charts, and fact-checks itself.

  --mode auto    Unattended/scheduled. Any section not 100% grounded is DROPPED, not
                 shipped with a caveat. Dropped sections logged to run_log_<date>.json.
  --mode review  Shows you each candidate section before you decide to include it.

Usage:
    python run_autonomous_report.py --mode auto
    python run_autonomous_report.py --mode review
    python run_autonomous_report.py --mode auto --dry-run   # replay cached scan

Requires ANTHROPIC_API_KEY always. Live discovery also needs web search access — see
agent/search_backend.py (free DuckDuckGo default, or TAVILY_API_KEY).
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "agent"))
from fact_check import check_draft
from render_report import render_report
from render_pdf import render_pdf
from trend_agent import discover_new_trends, check_known_trend
from write_section import write_section, extract_chart_data
from dynamic_chart import build_dynamic_chart

CHARTS_DIR = Path(__file__).resolve().parent / "charts" / "autonomous"

DEFAULT_DISCOVERY_QUERIES = [
    "European real estate emerging asset class 2026",
    "European commercial real estate new investment trend",
    "European logistics real estate market trend",
    "European residential build to rent trend",
]

KNOWN_THEMES_PATH = "agent/catella_march2026_trends.json"


def _log(run_log: list, event: str, **kwargs):
    entry = {"timestamp": datetime.now().isoformat(), "event": event, **kwargs}
    run_log.append(entry)
    print(f"[{event}]", " ".join(f"{k}={v}" for k, v in kwargs.items() if k != "chunks"))


def process_candidate(topic_brief: str, chunks: list[dict], run_log: list,
                       mode: str, chart_dir: Path) -> dict | None:
    try:
        draft = write_section(topic_brief, chunks)
    except Exception as e:
        _log(run_log, "draft_failed", topic=topic_brief, error=str(e))
        return None

    fc = check_draft(draft["body"], chunks)
    cited_chunks = [c for c in chunks if c["source_name"] in draft["body"]]

    chart_path = None
    chart_data = extract_chart_data(topic_brief, chunks)
    if chart_data:
        chart_dir.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(ch if ch.isalnum() else "_" for ch in draft["heading"])[:50]
        chart_path = build_dynamic_chart(chart_data, str(chart_dir / f"{safe_name}.png"))

    is_grounded = fc["coverage_score"] == 1.0

    if mode == "auto":
        if not is_grounded:
            _log(run_log, "auto_dropped", heading=draft["heading"],
                 reason=f"{len(fc['unverified_claims'])} unverified claim(s)",
                 unverified=fc["unverified_claims"])
            return None
        _log(run_log, "auto_accepted", heading=draft["heading"], coverage=fc["coverage_score"])
    else:
        print("\n" + "=" * 70)
        print(f"CANDIDATE SECTION: {draft['heading']}")
        print("=" * 70)
        print(draft["body"])
        print(f"\nGrounding: {fc['verdict']} (coverage {fc['coverage_score']:.0%})")
        if fc["unverified_claims"]:
            print(f"Unverified claims: {fc['unverified_claims']}")
        if chart_path:
            print(f"Chart saved to: {chart_path}")
        answer = input("\nInclude this section in the report? [y/N]: ").strip().lower()
        if answer != "y":
            _log(run_log, "human_rejected", heading=draft["heading"])
            return None
        _log(run_log, "human_accepted", heading=draft["heading"], coverage=fc["coverage_score"])

    return {
        "heading": draft["heading"], "body": draft["body"], "fact_check": fc,
        "chunks": cited_chunks, "chart_path": chart_path,
    }


def run(mode: str, dry_run: bool, discovery_queries: list[str]):
    run_log: list = []
    known_themes = json.loads(Path(KNOWN_THEMES_PATH).read_text(encoding="utf-8"))["themes"]

    candidates: list[tuple[str, list[dict]]] = []

    if dry_run:
        print("[dry-run] Replaying cached scan from agent/trend_scan_2026-08.json "
              "instead of live search.")
        from ingest import load_verified_facts
        all_facts = load_verified_facts("verified_facts_2026-08.json")
        all_chunk_dicts = [{"text": f.text, "source_name": f.source_name,
                             "source_url": f.source_url, "date": f.date} for f in all_facts]

        scan = json.loads(Path("agent/trend_scan_2026-08.json").read_text(encoding="utf-8"))
        for nt in scan["new_trends"]:
            if nt.get("is_new_trend"):
                matched_chunks = [
                    c for c in all_chunk_dicts
                    if any(c["source_name"] in citation for citation in nt["citations"])
                ]
                candidates.append((nt["trend_summary"], matched_chunks))
    else:
        print("=== Discovering new trends ===")
        findings = discover_new_trends(discovery_queries, known_themes)
        for f in findings:
            if f.get("is_new_trend") and f.get("confidence") != "low":
                candidates.append((f["trend_summary"], f["chunks"]))

        print("\n=== Checking known themes for updates ===")
        for theme in known_themes:
            result = check_known_trend(theme)
            if result["verdict"] in ("UPDATED", "CONTRADICTED"):
                brief = (f"Write an update to this thesis: {theme['summary']} "
                         f"New evidence suggests: {result['explanation']}")
                candidates.append((brief, result["chunks"]))

    print(f"\n{len(candidates)} candidate(s) to draft.\n")

    sections = []
    for topic_brief, chunks in candidates:
        section = process_candidate(topic_brief, chunks, run_log, mode, CHARTS_DIR)
        if section:
            sections.append(section)

    if not sections:
        print("\nNo sections passed grounding/review — no report generated this run.")
        Path(f"run_log_{date.today().isoformat()}.json").write_text(
            json.dumps(run_log, indent=2, default=str), encoding="utf-8")
        return

    common_kwargs = dict(
        title="Real Estate Market Research Update",
        subtitle=f"Autonomously generated — {date.today().isoformat()}",
        kicker=f"Autonomous run · mode={mode}" + (" · dry-run" if dry_run else ""),
        sections=sections,
        disclaimer=(
            "This report was generated autonomously by run_autonomous_report.py. "
            "Every claim was fact-checked against its cited source before inclusion; "
            f"sections that didn't fully pass grounding were {'dropped' if mode == 'auto' else 'excluded by human review'}, "
            "not shipped with a caveat. It is not an official publication of, and is "
            "not affiliated with or endorsed by, any organization referenced within it."
        ),
    )

    stamp = date.today().isoformat()
    html_path = render_report(out_path=f"autonomous_report_{stamp}.html", **common_kwargs)
    pdf_path = render_pdf(out_path=f"autonomous_report_{stamp}.pdf",
                           new_trend_section_ids=[s["heading"] for s in sections], **common_kwargs)

    Path(f"run_log_{stamp}.json").write_text(json.dumps(run_log, indent=2, default=str), encoding="utf-8")

    print(f"\n{len(sections)}/{len(candidates)} candidate section(s) included.")
    print(f"Written: {html_path}")
    print(f"Written: {pdf_path}")
    print(f"Run log: run_log_{stamp}.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["auto", "review"], default="auto")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--queries", type=str, default=None)
    args = parser.parse_args()

    queries = DEFAULT_DISCOVERY_QUERIES
    if args.queries:
        queries = [l.strip() for l in Path(args.queries).read_text().splitlines() if l.strip()]

    run(mode=args.mode, dry_run=args.dry_run, discovery_queries=queries)
