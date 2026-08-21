# Real Estate Market Research RAG

A RAG system for real estate research that won't hallucinate numbers — every claim is
cited to a real source or flagged as unverified, never guessed.

Daria Bystrova · AI Consulting Portfolio Project

---

## What this is

An independent prototype demonstrating a RAG architecture for institutional research
drafting: retrieves from primary sources, drafts with Claude, and fact-checks every
number before it ships. It is not an official publication of, and is not affiliated
with or endorsed by, any organization referenced within it. See `design_note.md`.

## Proof it works

**[`real_estate_market_research_update_2026-08.pdf`](real_estate_market_research_update_2026-08.pdf)**
(and matching `.html`/`.md`) — 6 sections, 6 charts, 100% of numeric claims traced to
a cited public source. Three genuinely new trends (data centers, life sciences real
estate, defense-driven industrial demand), and a rates/liquidity outlook that caught
something material: the ECB reversed into a hiking cycle in June 2026, directly
contradicting a continued-easing assumption.

## Architecture

```
sources (PDF/web/API) → ingest.py → chunks (source + date tagged)
chunks → retrieve.py → local embeddings (sentence-transformers, free, offline)
retrieved chunks + brief → generate_report.py (Claude) → draft, inline citations
draft → fact_check.py → every numeric claim checked against retrieved chunks
verified draft → render_report.py / render_pdf.py → styled HTML/PDF output
```

`build_trend_report.py` is the current hand-curated entry point. `run_autonomous_report.py`
discovers, drafts, and charts itself — see `agent/README.md` and `scheduling.md`.

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/dbystrova26/real-estate-market-research-rag.git
cd real-estate-market-research-rag
pip install -r requirements.txt
cp env.example .env    # add your ANTHROPIC_API_KEY

# Rebuild the full report (charts, 6 sections, PDF + HTML) — deterministic, no API call:
python build_trend_report.py

# Rebuild the shorter rates-only sample:
python build_sample_report.py

# Run the live Claude-drafting path on a new retrieval query:
python generate_report.py

# Run the fact-checker standalone against any draft text:
python fact_check.py

# Run the AUTONOMOUS agent:
python run_autonomous_report.py --mode review
python run_autonomous_report.py --mode auto
python run_autonomous_report.py --mode auto --dry-run
```

See `scheduling.md` for running the autonomous agent on a schedule.

## Sources it uses

| Source | Access | Status |
|---|---|---|
| ECB / Federal Reserve / Bank of England | Public | Live |
| Eurostat | Public API | Live |
| EU Commission policy documents | Public | Live |
| CBRE / Colliers press releases | Often public | Live, several used |
| Green Street, MSCI RCA, PMA, Oxford Economics | Paid subscription | Not connected — flagged, never estimated |

Full breakdown in `source_registry.md`.

## Project structure

```
real-estate-market-research-rag/
├── README.md, LICENSE, requirements.txt, env.example, .gitignore
├── methodology.md, use_case_definition.md, source_registry.md, design_note.md
├── ingest.py, retrieve.py, generate_report.py, fact_check.py
├── render_report.py, render_pdf.py, report_template.html
├── build_trend_report.py       # main entry point — 6 sections, charts, PDF+HTML
├── build_sample_report.py      # shorter deterministic sample
├── run_autonomous_report.py    # autonomous agent, auto/review modes
├── scheduling.md
├── charts/
│   ├── build_charts.py
│   └── *.png
├── agent/
│   ├── README.md
│   ├── search_backend.py, trend_agent.py, write_section.py, dynamic_chart.py
│   ├── catella_march2026_trends.json, trend_scan_2026-08.json
└── real_estate_market_research_update_2026-08.{html,pdf,md}
```

## Author

**Daria Bystrova** — AI Consulting Portfolio Project, 2026
[github.com/dbystrova26/real-estate-market-research-rag](https://github.com/dbystrova26/real-estate-market-research-rag)
