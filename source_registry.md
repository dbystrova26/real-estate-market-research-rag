# Source Registry

A house view like Catella's cites a mix of public and proprietary sources. This
registry maps common source types to whether they're publicly accessible today
(usable by this pipeline) or a paid institutional feed (stubbed, not faked).

| Source type | Used for | Public access? | Status here |
|---|---|---|---|
| Green Street Advisors (property price indices) | Price discovery, valuations | No — subscription | Not connected |
| MSCI RCA (Real Capital Analytics) | Investment volumes, liquidity | No — subscription | Not connected |
| PMA (Property Market Analysis) | Prime yields, prime rents | No — subscription | Not connected |
| Oxford Economics | GDP growth, rental forecasts | No — subscription | Not connected |
| Eurostat | Migration, demographic data | **Yes — public API** | Live, via `ingest.py` |
| European Commission documents | Affordable housing shortfall figures | **Yes — public document** | Live, ingestible |
| CBRE / Colliers / Savills press releases | Investment volumes, sector outlooks | **Yes — often public** | Live, several used |
| NATO / national government commitments | Defense spending targets | **Yes — public** | Live, used |

## Why this matters for "do not invent data"

This pipeline only generates claims grounded in retrieved chunks from public sources.
Where a claim would require a paid feed, the generator is instructed to write
`[DATA SOURCE NOT CONNECTED: <source name>]` rather than estimate a number — see
`methodology.md` → "Generation."

One methodology finding worth flagging: several figures initially assumed to require a
paid subscription (e.g. H1 2026 European transaction volumes) turned out to be
publicly reported in advisory-firm press releases (CBRE). Top-line figures are often
public even when granular, deal-level data is not — worth testing before assuming a
source is closed.
