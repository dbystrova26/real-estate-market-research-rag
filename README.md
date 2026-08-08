# Real Estate Market Research RAG

**A retrieval-augmented research assistant that would rather show you a gap than fill it with a guess.**

Most LLM-drafted research reads fluently and cites nothing. This project takes the opposite bet: every number Claude writes has to trace back to a real, dated, cited source — or the pipeline writes a visible `[DATA SOURCE NOT CONNECTED]` flag instead of a plausible-sounding figure. An independent fact-checker then re-verifies the draft against the retrieved sources before anything ships.

Built as a working prototype for real estate market research — the kind of "keep the house view current between publication cycles" work a research analyst does constantly.

---

## Why this exists

Institutional research has zero tolerance for a confidently-wrong number. Ask a general LLM "what's changed in European rates since March" and it will answer smoothly from training data of uncertain recency — sounding right is not the same as being right. This project constrains generation to *only* what's retrievable and citable, and checks that mechanically rather than trusting the model's word for it.

**Proof it works, not just a description of it:** [`rates_liquidity_update_2026-08.html`](rates_liquidity_update_2026-08.html) is a real, committed output — 100% of its numeric claims trace to a cited public source (ECB, US Federal Reserve, Bank of England, UK Parliament). It caught something genuinely material: the March 2026 report this project uses as a reference case assumed continuing rate cuts — but the **ECB actually reversed into a hiking cycle in June 2026**. The pipeline surfaced that contradiction instead of glossing over it, and flagged the two places where a full answer would need paid data feeds (Green Street, MSCI RCA, PMA) it doesn't have access to — rather than estimating them.

---

## How it works

```
sources (PDF / web / API)
        │
        ▼
   ingest.py          — parses PDFs, fetches web pages via Jina Reader (free, no API key),
        │                pulls Eurostat's public API. Every chunk keeps its source + date.
        ▼
  retrieve.py          — local, offline embeddings (sentence-transformers) + cosine
        │                similarity search. Zero marginal cost to re-run.
        ▼
generate_report.py     — Claude drafts the section, constrained by a system prompt that
        │                requires an inline citation for every claim, and a visible
        │                placeholder — never a guess — for anything not retrievable.
        ▼
 fact_check.py         — an independent second pass extracts every number in the draft
        │                and verifies it actually appears in a retrieved source chunk.
        ▼
render_report.py       — styled HTML output with a visible grounding score, so a reader
                          can see coverage at a glance, not just trust the byline.
```

Full detail on the grounding rules and the fact-checker's known limitations (it's a deliberately blunt numeric-substring check, not a full NLI classifier — documented honestly, not oversold) is in [`methodology.md`](methodology.md).

---

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/dbystrova26/real-estate-market-research-rag.git
cd real-estate-market-research-rag
pip install -r requirements.txt
cp env.example .env        # add your ANTHROPIC_API_KEY

# See the already-built, already-grounded sample report:
open rates_liquidity_update_2026-08.html

# Rebuild it yourself — deterministic, no API call needed:
python build_sample_report.py

# Run the live Claude-drafting path on a new retrieval query:
python generate_report.py

# Run the fact-checker standalone against any draft text:
python fact_check.py
```

---

## Sources it uses

This project's reference case is a real, public real estate house view — a good stand-in for the kind of report a research team needs to keep current. Of that report's 8 underlying data sources, this pipeline can only ground claims in the ones that are actually public:

| Source | Access | Status here |
|---|---|---|
| ECB / Federal Reserve / Bank of England policy decisions | **Public** | Live — ingested via `ingest.py` |
| Eurostat migration & population statistics | **Public API** | Live — ingested via `ingest.py` |
| EU Commission policy documents (e.g. Affordable Housing Plan) | **Public** | Ingestible as PDF/web via `ingest.py` |
| Green Street Advisors (European Property Price Index) | Paid subscription | Stubbed — flagged as `[DATA SOURCE NOT CONNECTED]`, never estimated |
| MSCI RCA (transaction volumes, liquidity) | Paid subscription | Stubbed |
| PMA (prime yields, prime rents) | Paid subscription | Stubbed |
| Oxford Economics (GDP/rental forecasts) | Paid subscription | Stubbed |

See [`source_registry.md`](source_registry.md) for the full breakdown, and [`use_case_definition.md`](use_case_definition.md) for who this is built for and what "done" looks like.

**Web ingestion** uses [Jina Reader](https://github.com/jina-ai/reader) — free, no API key — the same pattern used in [Agent-Reach](https://github.com/dbystrova26/Agent-Reach), which is where this project's web-reading approach comes from.

---

## Grounding, quantified

| Metric | Value |
|---|---|
| Numeric claims in the committed sample report | 17 |
| Claims traced to a cited public source | **17 (100%)** |
| Data gaps flagged rather than estimated | 2 |
| Distinct sources cited | 5 (ECB ×2, Federal Reserve, Bank of England, UK Parliament) |

---

## What's next

- **Multi-model comparison** — the same retrieval context run through ChatGPT, Gemini, DeepSeek, and Kimi, scored on *grounding coverage* rather than fluency. Claude is the generation model for phase 1; the multi-provider harness for phase 2 reuses the client pattern from a companion benchmark project.
- **Proprietary connectors** — the Green Street / MSCI RCA / PMA / Oxford Economics stubs get real implementations the moment there's institutional access to plug in.
- **Broader source ingestion** — more public feeds (national statistics offices, central bank research papers, regulatory filings) as the retrieval layer expands.

---

## A note on the reference case

This project uses a real, publicly available real estate house view as its test case because building against an actual professional deliverable — not a toy example — is what makes the grounding claims meaningful. No text, data, or branding from that report is reproduced here; see [`design_note.md`](design_note.md) for the reasoning behind keeping this project's visual style and content independent of it. This is a personal prototype, not an official publication of, or affiliated with, the organization whose report it references.

---

## Author

**Daria Bystrova** — AI Consulting Portfolio Project, 2026
[github.com/dbystrova26/real-estate-market-research-rag](https://github.com/dbystrova26/real-estate-market-research-rag)
