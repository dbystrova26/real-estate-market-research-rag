# Methodology

## Pipeline

```
sources (PDF/web/API) → rag/ingest.py → chunks
chunks → rag/chunk_embed.py → local embeddings (sentence-transformers, offline, no API cost)
query/section brief → rag/retrieve.py → top-k relevant chunks, each tagged with source + date
retrieved chunks + section brief → rag/generate_report.py (Claude) → draft section, inline citations
draft → rag/fact_check.py → every numeric/factual claim checked against retrieved chunks
verified draft → rag/render_report.py → styled HTML/PDF matching institutional report conventions
```

## Ingestion (`rag/ingest.py`)

Three input types, each parsed to plain text + metadata (source name, URL, publish date):

- **PDF** (e.g. the baseline House View itself) — parsed with `pdfplumber`, page-level chunks
- **Web pages** (ECB/BOE/Fed press releases, EU Affordable Housing Plan) — fetched via
  [Jina Reader](https://github.com/jina-ai/reader) (`https://r.jina.ai/<url>`), a free,
  no-API-key reader service that returns clean text from a URL. This ingestion pattern is
  the same one used in [Agent-Reach](https://github.com/dbystrova26/Agent-Reach), which
  is what this project uses as its web-reading layer rather than a bespoke scraper.
- **APIs** (Eurostat, ECB Data Portal) — direct JSON via their public REST endpoints

Every chunk is stored with `{text, source_name, source_url, date, source_type}`. No chunk
is ever created without a traceable source — this is what makes the grounding check
possible downstream.

## Embedding & retrieval

Chunks are embedded with `sentence-transformers/all-MiniLM-L6-v2` — a small, free, offline
model, chosen deliberately over a paid embeddings API so the pipeline has zero marginal
cost to run repeatedly during development. Retrieval is cosine similarity top-k (default
k=8) against the section brief being drafted.

## Generation (`rag/generate_report.py`) — Claude, grounding-constrained

The generation prompt enforces three rules, verbatim in the system prompt:

1. Every factual claim (a number, a date, a named event) must be traceable to one of the
   retrieved chunks. Cite it inline as `(Source: <name>, <date>)`.
2. If the section brief calls for information not present in any retrieved chunk, write
   `[DATA SOURCE NOT CONNECTED: <what's missing>]` instead of estimating, inferring, or
   drawing on general world knowledge.
3. Do not smooth over contradictions between sources — if two retrieved chunks disagree,
   state both and flag the discrepancy rather than picking one silently.

This is the same "ground or flag, never invent" principle used in the report's own no-
fabrication instruction — the pipeline is built to fail loudly (a visible placeholder)
rather than fail silently (a plausible-sounding invented number).

## Fact-checking (`rag/fact_check.py`)

A second pass, independent of the generator, that:

- Extracts every number and named claim from the draft (regex + simple NER)
- Searches the retrieved chunk set for a matching value/claim
- Flags anything in the draft that isn't traceable back to a chunk as `UNVERIFIED`
- Outputs a coverage score: `% of factual claims with a verified source`

This is a blunt, imperfect check (it can miss paraphrased claims and can't verify a
citation is used *correctly*, only that the cited fact appears somewhere in context) —
documented here rather than oversold, same as the fact-check limitations in the companion
LLM benchmark project.

## Rendering (`rag/render_report.py`)

Output styling echoes the typographic conventions of institutional real estate research —
a serif display headline, clean sans-serif body, a colored accent bar per section, pull-quote
sidebar — using open, freely-licensed fonts (Source Serif 4 for headlines, Inter for body)
rather than Catella's actual (unknown, likely licensed) corporate typeface, and a neutral
navy/charcoal palette rather than Catella's red brand mark. See `docs/design_note.md`
for why the exact brand identity is deliberately not reproduced.

## Known limitations

- Fact-checker is regex-based, not a full grounding classifier — treat its output as a
  useful flag, not a certification
- Public sources cover macro/policy and demographic data well; proprietary feeds (pricing,
  yields, transaction volumes) are the majority of what makes a house view distinctive,
  and this prototype cannot fill that gap without real Catella data access
- Embedding model is small and general-purpose; retrieval quality on dense real-estate
  jargon would improve with a domain-tuned or larger model, traded off here for zero cost
- This is a portfolio prototype built in days, not a production research tool — the value
  being demonstrated is the grounding architecture and the discipline of the no-fabrication
  constraint, not a finished product
