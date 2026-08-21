# Methodology

## Pipeline

```
sources (PDF/web/API) → ingest.py → chunks
chunks → retrieve.py → local embeddings (sentence-transformers, offline, no API cost)
query/section brief → generate_report.py (Claude) → draft section, inline citations
draft → fact_check.py → every numeric/factual claim checked against retrieved chunks
verified draft → render_report.py / render_pdf.py → styled HTML/PDF output
```

`build_trend_report.py` is the current hand-curated entry point (fixed set of
sections, each with 3 paragraphs of analysis and a supporting chart).
`run_autonomous_report.py` is the fully autonomous version — see `agent/README.md`.

## Ingestion (`ingest.py`)

Three input types, each parsed to plain text + metadata (source name, URL, publish date):

- **PDF** — parsed with `pdfplumber`, page-level chunks
- **Web pages** — fetched via [Jina Reader](https://github.com/jina-ai/reader)
  (`https://r.jina.ai/<url>`), free, no API key. Same pattern used in
  [Agent-Reach](https://github.com/dbystrova26/Agent-Reach).
- **APIs** (Eurostat) — direct JSON via public REST endpoints

Every chunk is stored with `{text, source_name, source_url, date, source_type}` — no
chunk is ever created without a traceable source.

## Embedding & retrieval

Chunks are embedded with `sentence-transformers/all-MiniLM-L6-v2` — small, free,
offline. Retrieval is cosine similarity top-k against the section brief.

## Generation — grounding-constrained

The generation prompt enforces:
1. Every factual claim must cite a retrieved chunk inline: `(Source: <name>, <date>)`.
2. Missing data → `[DATA SOURCE NOT CONNECTED: <what's missing>]`, never estimated.
3. Contradictions between sources are surfaced, not silently resolved.

## Fact-checking (`fact_check.py`)

A second pass, independent of the generator:
- Extracts every number and named claim from the draft (regex-based)
- Checks each against the retrieved chunk set
- Flags anything not traceable as `UNVERIFIED`
- Outputs a coverage score

Blunt by design — a substring match, not a full NLI grounding classifier. It can miss
paraphrased claims and can't verify a citation is used *correctly*, only that the cited
fact appears somewhere in context.

## Rendering

`render_report.py` (HTML) and `render_pdf.py` (PDF, via reportlab — chosen over
WeasyPrint/wkhtmltopdf to avoid native library install failures on Windows) both use
one font family throughout (Inter/Helvetica), justified body text, and skip
`[DATA SOURCE NOT CONNECTED]` placeholder paragraphs entirely rather than showing them
as visible gaps — those gaps are documented here and in `source_registry.md` instead.

## Known limitations

- Fact-checker is regex-based, not a full grounding classifier
- Public sources cover macro/policy/demographic data well; proprietary feeds (pricing,
  yields, transaction volumes) are the majority of what makes a house view distinctive
- Embedding model is small and general-purpose
- This is a portfolio prototype, not a finished production tool
