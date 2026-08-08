# Source Registry

The March 2026 Catella House View cites 8 footnoted sources. This registry maps each one
to whether it's publicly accessible (usable by this pipeline today) or a paid institutional
feed (usable once you have Catella-level data access — the connector is stubbed, not faked).

| # | Source (as cited in the report) | Used for | Public access? | This repo's status |
|---|---|---|---|---|
| 1 | Green Street Advisors, European Property Price Index (CPPI) | Peak-to-trough property values, price discovery | No — subscription | `connectors/green_street.py` stubbed, raises `NotConfiguredError` |
| 2 | MSCI RCA (Real Capital Analytics) | Investment volumes, liquidity, transaction trends | No — subscription | `connectors/msci_rca.py` stubbed |
| 3 | PMA (Property Market Analysis) | Prime yields, prime rents (98 market segments) | No — subscription | `connectors/pma.py` stubbed |
| 4 | Oxford Economics | GDP growth outlook, rental forecasts | No — subscription | `connectors/oxford_economics.py` stubbed |
| 5 | ECB / Federal Reserve / Bank of England websites | Central bank policy rates | **Yes — public** | Live: `connectors/central_banks.py` |
| 6 | Eurostat migration and population statistics | Urban migration, demographic growth | **Yes — public API** | Live: `connectors/eurostat.py` |
| 7 | European Commission: The European Affordable Housing Plan (Dec 2025) | Affordable housing shortfall figures | **Yes — public document** | Live: ingestible via `rag/ingest.py` |
| 8 | PMA prime rents (office/industrial/retail, 98 segments) | Pricing momentum chart | No — subscription | `connectors/pma.py` stubbed |

## Why this matters for "do not invent data"

3 of 8 of Catella's own sources are freely public. This pipeline only generates claims
grounded in retrieved chunks from sources 5, 6, 7 (plus any public news/press releases
ingested via `rag/ingest.py`) until proprietary connectors are configured with real
credentials. Where a claim would require a stubbed source, the generator is instructed
to write `[DATA SOURCE NOT CONNECTED: <source name>]` rather than estimate a number —
see `docs/methodology.md` → "Grounding enforcement."

## Additional public sources added in this update (not in the original report)

These weren't cited by Catella but are directly relevant to updating the report's rates
thesis for August 2026 — see `data/verified_facts_2026-08.json` for the sourced facts:

- ECB monetary policy decisions (press releases, June & July 2026)
- Federal Reserve Implementation Notes (July 2026)
- Bank of England Monetary Policy Summary and Minutes (July 2026)
- UK House of Commons Library briefing on interest rates and monetary policy
