# Use Case Definition

## Context

Catella publishes a House View twice a year — a synthesized market outlook drawing on
proprietary data feeds (Green Street, MSCI RCA, PMA, Oxford Economics) and the research
team's own judgment. Between publications, the world doesn't wait: rates move, deals
close, policy shifts. This project is a working prototype of a tool a research analyst
could use to keep a house view "live" between formal publication cycles — not to replace
analyst judgment, but to do the grinding first pass: watch the sources, flag what's
changed, draft the update with citations attached, and hand the analyst a starting point
they can trust because every claim traces back to a real source.

## Why RAG, specifically

A general-purpose LLM asked "what's happened in European real estate rates since March"
will answer from training data of uncertain recency and mix in things that sound plausible
but aren't sourced. For institutional research, that's not good enough — a wrong number in
a house view is a credibility problem, not just an inconvenience. Retrieval-augmented
generation constrains the model to only assert what's actually in a retrieved, dated,
sourced document, and this project's fact-checker (`rag/fact_check.py`) enforces that
constraint mechanically rather than trusting the model's honesty alone.

## Target user

A real estate research analyst (the role I'm applying for) who wants to:

1. Feed in a prior house view (or any market report) as a baseline
2. Point the pipeline at the same primary sources the original report used
3. Get back a **draft update** — what's changed, what's confirmed, what needs a fresh
   analyst call — with every factual claim citable to a specific source and date
4. Extend the source list beyond what the original report used, when something material
   happens that the original sources wouldn't have caught yet (e.g. a geopolitical shock)

## What "done" looks like for this prototype

- Ingests the March 2026 Catella House View as a baseline document (via `rag/ingest.py`)
- Ingests the report's own footnoted public sources (ECB/Fed/BOE, Eurostat, EU Affordable
  Housing Plan) plus any new public sources relevant to changes since March
- Retrieves and cites specific passages rather than summarizing from memory
- Flags every section where a proprietary data feed (Green Street, MSCI RCA, PMA, Oxford
  Economics) would be needed to fully update the analysis, rather than guessing at what
  those feeds would show
- Produces one real, fully-grounded worked example: a rates & liquidity update, since
  that's the one area where all the needed sources are public — see
  `reports/sample/rates_liquidity_update_2026-08.md`

## Phase 2 (not built yet, scaffolded)

Once the RAG + grounding pipeline is proven on Claude, the same source-retrieval layer
feeds identical prompts to ChatGPT, Gemini, DeepSeek, and Kimi to compare which model
stays best-grounded (lowest ungrounded-claim rate) under the same retrieval context —
reusing the multi-provider client pattern from the companion
[llm-real-estate-benchmark](https://github.com/dbystrova26/llm-real-estate-benchmark)
project. Grounding quality, not raw fluency, is the metric that matters for this use case.
