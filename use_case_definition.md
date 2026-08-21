# Use Case Definition

## Context

A house view like Catella's is published twice a year — a synthesized market outlook
drawing on proprietary data feeds and the research team's own judgment. Between
publications, the world doesn't wait: rates move, deals close, policy shifts. This
project is a working prototype of a tool a research analyst could use to keep a house
view "live" between formal publication cycles — not to replace analyst judgment, but to
do the grinding first pass: watch the sources, flag what's changed, draft the update
with citations attached.

## Why RAG, specifically

A general-purpose LLM asked "what's happened in European real estate investment since
March" will answer from training data of uncertain recency and mix in things that
sound plausible but aren't sourced. Retrieval-augmented generation constrains the
model to only assert what's actually in a retrieved, dated, sourced document, and this
project's fact-checker (`fact_check.py`) enforces that constraint mechanically rather
than trusting the model's honesty alone.

## Target user

A real estate research analyst who wants to:
1. Feed in a prior house view (or any market report) as a baseline
2. Point the pipeline at the same primary sources the original report used
3. Get back a draft update — what's changed, what's confirmed — with every factual
   claim citable to a specific source and date
4. Extend the source list when something material happens the original sources
   wouldn't have caught yet

## What "done" looks like for this prototype

- Ingests a baseline house view as reference (via `ingest.py`)
- Ingests public sources (Eurostat, EU Commission documents, industry press releases)
- Retrieves and cites specific passages rather than summarizing from memory
- Flags where a proprietary data feed would be needed, rather than guessing
- Produces real, fully-grounded worked examples — see `real_estate_market_research_update_2026-08.{html,pdf,md}`

## Phase 2: multi-model comparison

Claude is the generation model for this phase. The next step is running the same
retrieval context through ChatGPT, Gemini, DeepSeek, and Kimi and comparing which
model stays best-grounded under identical context — reusing the multi-provider client
pattern from the companion
[llm-real-estate-benchmark](https://github.com/dbystrova26/llm-real-estate-benchmark)
project. Grounding quality, not raw fluency, is the metric that matters here.
