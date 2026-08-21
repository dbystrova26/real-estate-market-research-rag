# The Trend Agent

## Two ways to use it

1. **Manual/curated** (`build_trend_report.py` at repo root): review findings and
   hand-write section prose, as done for the current committed report.
2. **Fully autonomous** (`run_autonomous_report.py` at repo root): the agent
   discovers, drafts, charts, and fact-checks itself. `--mode auto` self-gates on
   grounding (safe for scheduled runs); `--mode review` asks before including each
   section. See `../scheduling.md`.

## Search backend

`search_backend.py`: DuckDuckGo HTML scrape by default (free, no key), or set
`TAVILY_API_KEY` for a more reliable production search API. Page reading uses Jina
Reader (free, no key) — same pattern as
[Agent-Reach](https://github.com/dbystrova26/Agent-Reach).

## Autonomous drafting

- **`write_section.py`** drafts 3-paragraph analytical prose (facts → implications →
  positioning) directly from retrieved chunks, under the same grounding rules used
  elsewhere. `extract_chart_data()` pulls 2-5 chartable numbers, flagging any derived
  figure, or returns nothing rather than forcing a chart.
- **`dynamic_chart.py`** plots whatever was extracted, matching the style of the
  hand-built charts.

## Why there's a cached result file

`trend_scan_2026-08.json` is a real output — the searches it describes were actually
run and sources actually retrieved and cited. Checked in so the pipeline has something
genuine to demo on a first run without requiring search access configured yet.

## Known limitations

- DuckDuckGo scraping is brittle (screen-scraping an HTML endpoint, not a documented API)
- "New" is judged against a hand-written 7-theme baseline, not the full text of any
  original report
- The judge model's verdict is a judgment call, not a fact — treat `confidence: low`
  results with real skepticism
