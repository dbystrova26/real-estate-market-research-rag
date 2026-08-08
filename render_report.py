"""
Takes generated section text + its fact-check result and renders the styled HTML report.
Deliberately does not use Catella's logo or exact typeface — see docs/design_note.md.
"""

import html
import re
from datetime import date
from pathlib import Path

TEMPLATE_PATH = Path(__file__).resolve().parent / "report_template.html"


def _format_body(text: str) -> str:
    """Wrap [DATA SOURCE NOT CONNECTED: ...] placeholders in a styled div (as their own
    block, not nested in <p>), regular paragraphs in <p>."""
    escaped = html.escape(text)
    paragraphs = [p.strip() for p in escaped.split("\n\n") if p.strip()]
    out = []
    for p in paragraphs:
        placeholder_match = re.fullmatch(r"\[DATA SOURCE NOT CONNECTED:(.*?)\]", p, re.DOTALL)
        if placeholder_match:
            out.append(f'<div class="placeholder">⚠ Data source not connected:{placeholder_match.group(1)}</div>')
        else:
            out.append(f"<p>{p}</p>")
    return "\n".join(out)


def render_report(title: str, subtitle: str, kicker: str,
                   sections: list[dict], disclaimer: str,
                   out_path: str) -> str:
    """
    sections: list of {"heading": str, "body": str, "fact_check": dict, "chunks": list[dict]}
    """
    all_sources = {}
    section_html_parts = []
    total_claims, total_grounded = 0, 0

    for sec in sections:
        fc = sec.get("fact_check", {})
        total_claims += fc.get("n_claims_checked", 0)
        total_grounded += fc.get("n_grounded", 0)

        badge_class = "pass" if fc.get("coverage_score", 1.0) == 1.0 else "review"
        badge_text = fc.get("verdict", "not checked")
        if fc.get("n_claims_checked", 0) == 0 and fc.get("placeholders_used", 0) > 0:
            badge_class = "gated"
            badge_text = "NO PUBLIC SOURCE — section gated, nothing estimated"

        section_html_parts.append(
            f'<h2>{html.escape(sec["heading"])}</h2>\n'
            f'<span class="grounding-badge {badge_class}">{html.escape(badge_text)}</span>\n'
            f'{_format_body(sec["body"])}'
        )

        for chunk in sec.get("chunks", []):
            all_sources[chunk["source_name"]] = chunk.get("source_url", "")

    overall_coverage = round(total_grounded / total_claims, 3) if total_claims else 1.0
    grounding_summary = (
        f'<div class="pullquote">Grounding check: {total_grounded}/{total_claims} numeric '
        f'claims across this report traced to a cited source ({overall_coverage:.0%} coverage). '
        f'See docs/methodology.md for how this check works and its limitations.</div>'
    ) if total_claims else ""

    source_list_html = "\n".join(
        f'<li>{html.escape(name)}'
        + (f' — <a href="{html.escape(url)}">{html.escape(url)}</a>' if url else '')
        + '</li>'
        for name, url in sorted(all_sources.items())
    )

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    rendered = (
        template
        .replace("{{title}}", html.escape(title))
        .replace("{{subtitle}}", html.escape(subtitle))
        .replace("{{kicker}}", html.escape(kicker))
        .replace("{{generated_meta}}", f"Generated {date.today().isoformat()} · Claude-drafted, RAG-grounded")
        .replace("{{grounding_summary}}", grounding_summary)
        .replace("{{sections}}", "\n".join(section_html_parts))
        .replace("{{source_list}}", source_list_html)
        .replace("{{disclaimer}}", html.escape(disclaimer))
    )

    Path(out_path).write_text(rendered, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    demo = render_report(
        title="Rates & Liquidity Update",
        subtitle="A grounded update to the March 2026 House View",
        kicker="Independent research prototype — August 2026",
        sections=[{
            "heading": "What's changed since March",
            "body": "The ECB raised its deposit facility rate to 2.25% on 17 June 2026 "
                    "(Source: ECB, 2026-06-11).",
            "fact_check": {"n_claims_checked": 1, "n_grounded": 1, "coverage_score": 1.0,
                            "verdict": "PASS — all numeric claims traced to a source"},
            "chunks": [{"source_name": "ECB — Monetary policy decision",
                        "source_url": "https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260611~4d41bd5e83.en.html"}],
        }],
        disclaimer="Independent portfolio prototype. Not an official Catella publication "
                   "and not affiliated with or endorsed by Catella AB.",
        out_path="/tmp/demo_report.html",
    )
    print(f"Demo report written to {demo}")
