"""
Renders section data into the styled HTML report. One font family (Inter) throughout;
placeholder ([DATA SOURCE NOT CONNECTED]) paragraphs are skipped entirely rather than
shown as visible gaps. No grounding badges/jargon shown to the reader — fact_check.py
still runs internally, it's just not displayed. See design_note.md.
"""

import html
import re
from datetime import date
from pathlib import Path

TEMPLATE_PATH = Path(__file__).resolve().parent / "report_template.html"


def _format_body(text: str) -> str:
    escaped = html.escape(text)
    paragraphs = [p.strip() for p in escaped.split("\n\n") if p.strip()]
    out = []
    for p in paragraphs:
        if re.fullmatch(r"\[DATA SOURCE NOT CONNECTED:(.*?)\]", p, re.DOTALL):
            continue
        out.append(f"<p>{p}</p>")
    return "\n".join(out)


def render_report(title: str, subtitle: str, kicker: str,
                   sections: list[dict], disclaimer: str,
                   out_path: str) -> str:
    """sections: list of {"heading", "body", "fact_check", "chunks"}"""
    all_sources = {}
    section_html_parts = []

    for sec in sections:
        section_html_parts.append(
            f'<h2>{html.escape(sec["heading"])}</h2>\n'
            f'{_format_body(sec["body"])}'
        )
        for chunk in sec.get("chunks", []):
            all_sources[chunk["source_name"]] = chunk.get("source_url", "")

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
        .replace("{{sections}}", "\n".join(section_html_parts))
        .replace("{{source_list}}", source_list_html)
        .replace("{{disclaimer}}", html.escape(disclaimer))
    )

    Path(out_path).write_text(rendered, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    demo = render_report(
        title="Data Center Update",
        subtitle="A grounded update on European data center vacancy",
        kicker="Independent research prototype",
        sections=[{
            "heading": "What's changed",
            "body": "European data center vacancy fell below 10% in late 2024 "
                    "(Source: CBRE, 2026-01-01).",
            "fact_check": {"n_claims_checked": 1, "n_grounded": 1, "coverage_score": 1.0,
                            "verdict": "PASS"},
            "chunks": [{"source_name": "CBRE",
                        "source_url": "https://www.cbre.com"}],
        }],
        disclaimer="Independent portfolio prototype.",
        out_path="/tmp/demo_report.html",
    )
    print(f"Demo report written to {demo}")
