# Real Estate Market Research RAG

A research tool that drafts real estate market analysis and refuses to make numbers
up. Every figure in its output is either traced back to a real, dated source, or
openly flagged as unverified — never silently guessed.

**Daria Bystrova** · AI Consulting Portfolio Project

---

## What this is, in plain terms

Real estate research teams publish periodic market outlooks — reports that combine
paid data feeds with the team's own judgment. Between publications, the market
doesn't stand still: policy shifts, deals close, new asset classes emerge. This
project is a prototype of a tool that helps keep that kind of research current — it
searches for what's changed, drafts an analysis in plain professional language, and
**checks its own work** before anything gets included.

The technique behind it is called **RAG — Retrieval-Augmented Generation**. In plain
English: instead of asking an AI model to "just know" facts from memory (which can be
outdated or simply wrong), the system first *retrieves* real documents and articles,
then *generates* its analysis strictly from what it just retrieved — with a citation
attached to every claim. A second, independent step then re-checks every number in the
draft against those same sources and flags anything that doesn't match. If a topic
needs data this system doesn't have access to, it says so explicitly instead of
inventing a plausible-sounding figure.

## What you get from running it

A finished, formatted report — as a webpage, a PDF, and plain text — covering:

- **Three genuinely new real estate trends** the tool identified on its own: data
  centers as an emerging institutional asset class, life sciences real estate, and
  defense/rearmament-driven industrial demand
- **Capital flows analysis** — where European real estate investment is actually
  going right now, and what shifted
- **A structural housing-supply analysis** grounded in EU policy data

Every section carries a supporting chart built only from numbers that trace back to a
cited source. Nothing in the finished report is estimated or invented.

## Sources it uses

| Type | Examples | Access |
|---|---|---|
| Central real estate advisory firms | CBRE, Colliers | Public — press releases and published sector guides |
| EU policy institutions | European Commission, Joint Research Centre | Public documents |
| Industry/market bodies | European Data Centre Association | Public reporting |
| Defense/policy sources | NATO commitments, government spending plans | Public reporting |
| Institutional data feeds (yields, transaction-level detail) | Green Street, MSCI RCA, PMA, Oxford Economics | **Paid subscriptions — not connected.** The system flags where these would add detail, rather than guessing. |

Full breakdown in [`source_registry.md`](source_registry.md).

---

## How to run it — no prior experience assumed

You don't need to know what RAG is or have used Python before. This walks through
every step.

### Step 1: Install two free programs

1. **Python** — the programming language this project is written in. Download from
   [python.org/downloads](https://python.org/downloads) (get version 3.10 or newer)
   and run the installer. On the first screen, check the box that says **"Add
   Python to PATH"** before clicking Install.
2. **Git** — used to download the project files. Download from
   [git-scm.com/downloads](https://git-scm.com/downloads) and install with default
   options.

### Step 2: Open a terminal

- **Windows**: press the Windows key, type `cmd`, press Enter (or use "Git Bash",
  installed alongside Git)
- **Mac**: press Cmd+Space, type `terminal`, press Enter

### Step 3: Download the project

Copy and paste this into the terminal, then press Enter:

```bash
git clone https://github.com/dbystrova26/real-estate-market-research-rag.git
cd real-estate-market-research-rag
```

### Step 4: Install the project's dependencies

Still in the same terminal:

```bash
pip install -r requirements.txt
```

This downloads the handful of free code libraries the project relies on. It can take
a minute or two the first time.

### Step 5: See the finished report immediately

No setup needed for this step — a complete, already-generated report is included in
the project:

```bash
# Windows:
start real_estate_market_research_update_2026-08.pdf
# Mac:
open real_estate_market_research_update_2026-08.pdf
```

That opens the PDF you'd see if you ran the whole pipeline yourself.

### Step 6 (optional): Regenerate the report yourself

This re-runs the whole pipeline — grounding checks and all — and rebuilds the same
report from scratch:

```bash
python build_trend_report.py
```

You'll see each section print a `PASS` line as it's checked. This step needs no API
key — it uses a pre-written, already-source-checked draft, so it's free to run.

### Step 7 (optional): Run it live with Claude

To have the system draft genuinely new analysis (not the pre-written sample), you
need an Anthropic API key:

1. Get a key at [console.anthropic.com](https://console.anthropic.com)
2. Copy the settings template: `cp env.example .env` (Mac) or `copy env.example .env`
   (Windows)
3. Open the new `.env` file in any text editor and paste your key after
   `ANTHROPIC_API_KEY=`
4. Run: `python generate_report.py`

### Step 8 (optional): Run the fully autonomous agent

This is the most advanced part — a version that searches the web itself, decides
what's newsworthy, drafts it, charts it, and checks its own grounding without a human
picking the topics:

```bash
python run_autonomous_report.py --mode review
```

`--mode review` shows you each finding before including it. See
[`scheduling.md`](scheduling.md) for running this unattended on a schedule (e.g.
every Monday morning).

---

## Every file in this project, and what it does

### Root-level documents

| File | What it is |
|---|---|
| `README.md` | This file |
| `LICENSE` | MIT license — the code is free to reuse |
| `requirements.txt` | The list of free code libraries this project needs (used automatically by Step 4 above) |
| `env.example` | A template for API keys — copy to `.env` and fill in your own |
| `.gitignore` | Tells the file-tracking system which files not to save (e.g. your private `.env`) |
| `methodology.md` | The detailed technical explanation of how the grounding/fact-checking works |
| `use_case_definition.md` | Who this tool is built for and what "success" means for it |
| `source_registry.md` | Which data sources are public (usable today) vs. paid subscriptions (not connected) |
| `design_note.md` | Explains the visual/branding choices and why no company's exact branding is copied |
| `scheduling.md` | How to set this up to run automatically on a schedule |

### The finished report (already generated, ready to open)

| File | What it is |
|---|---|
| `real_estate_market_research_update_2026-08.pdf` | The finished report, formatted for printing/sharing |
| `real_estate_market_research_update_2026-08.html` | The same report as a webpage — open in any browser |
| `real_estate_market_research_update_2026-08.md` | The same report as plain text |

### The pipeline itself (the actual "engine")

| File | What it does, in plain terms |
|---|---|
| `ingest.py` | Reads in source material — PDFs, web pages, or public data feeds — and breaks it into small, labeled chunks, each tagged with exactly where it came from |
| `retrieve.py` | Searches through those chunks to find the ones relevant to whatever topic is being written about (this is the "R" in RAG) |
| `generate_report.py` | Sends the relevant chunks to Claude and asks it to write a section — but under strict instructions to cite every fact and never state anything the chunks don't support (this is the "G" in RAG) |
| `fact_check.py` | The independent double-check: re-reads the draft afterward and verifies every number in it actually appears in a real source, flagging anything that doesn't |
| `render_report.py` | Turns a finished, checked draft into the formatted webpage (`.html`) version |
| `render_pdf.py` | Turns a finished, checked draft into the formatted PDF version |
| `report_template.html` | The visual template (fonts, colors, layout) used by `render_report.py` |
| `verified_facts_2026-08.json` | The underlying set of real, sourced facts this report's content is built from — every entry includes a link to where it came from |
| `build_trend_report.py` | **The main script** — assembles everything above into the finished 5-section report you see in the PDF |

### `charts/` — the visual charts in the report

| File | What it does |
|---|---|
| `build_charts.py` | Generates every chart in the report — each one is built strictly from a cited number, or a clearly-labeled simple calculation from one (e.g. converting a percentage into a total) |
| `*.png` | The chart images themselves, already generated and embedded in the report |

### `agent/` — the fully autonomous version

| File | What it does |
|---|---|
| `README.md` | Explains this folder in more detail |
| `search_backend.py` | Searches the public web for real estate news and data (no paid search subscription required) |
| `trend_agent.py` | Reads what the search found and judges whether it's a genuinely new trend, or an update to something already known |
| `write_section.py` | Has Claude draft a report section from what the agent found — same strict "cite everything" rules as `generate_report.py` |
| `dynamic_chart.py` | Builds a chart from whatever numbers the agent found, on the fly |
| `catella_march2026_trends.json` | A short reference list of established real estate themes, used so the agent can judge what counts as "new" |
| `trend_scan_2026-08.json` | A real, saved example of what the agent found on an actual run — lets you see the autonomous pipeline's output without needing to run a live web search yourself |

### Top-level autonomous entry point

| File | What it does |
|---|---|
| `run_autonomous_report.py` | Runs the entire autonomous pipeline end-to-end: search → judge → draft → chart → fact-check → either publish or flag for review |

---

## How the grounding actually works (short version)

1. Every source gets broken into small chunks, each permanently tagged with where it
   came from and when
2. When drafting a section, Claude is only shown the relevant chunks and told: cite
   every fact, or say plainly that the data isn't available — never guess
3. After drafting, a separate, independent script re-reads the draft and checks every
   number against the source chunks
4. Anything that doesn't check out is flagged — in the autonomous version, it's
   dropped from the report entirely rather than published with a caveat

This project's current report: **100% of numeric claims trace to a cited public
source**, across all 5 sections.

---

## What this demonstrates

- Building a real, working retrieval-augmented generation system, not just prompting
  a chatbot
- Designing for trustworthiness first — a system that visibly refuses to guess is
  more useful for institutional research than one that always sounds confident
- Independent verification as a first-class step, not an afterthought
- A path to full automation (the `agent/` folder) with a human-in-the-loop option
  built in from the start, not bolted on later

## Author

**Daria Bystrova** — AI Consulting Portfolio Project, 2026
[github.com/dbystrova26/real-estate-market-research-rag](https://github.com/dbystrova26/real-estate-market-research-rag)

*Independent prototype. Not affiliated with or endorsed by any organization
referenced within it.*
