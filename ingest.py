"""
Ingests source documents into a common chunk format:
    {"text": str, "source_name": str, "source_url": str, "date": str, "source_type": str}

Every chunk MUST carry a source_name + source_url. This is what makes fact_check.py
possible downstream — a chunk with no traceable source should never be created.

Three ingestion paths:
  - ingest_pdf(path, source_name)         : local PDF (e.g. a baseline house view)
  - ingest_web(url, source_name)          : any public URL, via Jina Reader (free, no key)
  - ingest_eurostat(dataset_code, ...)     : Eurostat public REST API

Web reading via Jina Reader (https://r.jina.ai/<url>) follows the same free, no-API-key
pattern documented in https://github.com/dbystrova26/Agent-Reach's web channel — this
project doesn't install that CLI, but reuses its choice of ingestion tool.
"""

import json
import re
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path

import requests


@dataclass
class Chunk:
    text: str
    source_name: str
    source_url: str
    date: str
    source_type: str  # "pdf" | "web" | "api"


def ingest_pdf(path: str, source_name: str, source_url: str = "", published: str = "") -> list[Chunk]:
    """Chunk a local PDF page by page. Requires pdfplumber."""
    import pdfplumber

    chunks = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            chunks.append(Chunk(
                text=text,
                source_name=f"{source_name} (p.{i + 1})",
                source_url=source_url,
                date=published or str(date.today()),
                source_type="pdf",
            ))
    return chunks


def ingest_web(url: str, source_name: str, published: str = "", timeout: int = 20) -> list[Chunk]:
    """Fetch a public URL via Jina Reader and split into paragraph chunks.
    No API key required — Jina Reader is a free public reading service."""
    reader_url = f"https://r.jina.ai/{url}"
    resp = requests.get(reader_url, timeout=timeout)
    resp.raise_for_status()
    text = resp.text

    # split on double newlines, drop very short fragments (nav junk etc.)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 80]

    return [
        Chunk(
            text=p,
            source_name=source_name,
            source_url=url,
            date=published or str(date.today()),
            source_type="web",
        )
        for p in paragraphs
    ]


def ingest_eurostat(dataset_code: str, source_name: str, params: dict | None = None,
                     timeout: int = 20) -> list[Chunk]:
    """Pull a Eurostat dataset via the public statistics API and turn it into one
    descriptive chunk (Eurostat's raw JSON is not directly prose-readable, so this
    summarizes it into a citable text block rather than dumping raw numbers)."""
    base = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset_code}"
    resp = requests.get(base, params=params or {}, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()

    summary = (
        f"Eurostat dataset {dataset_code} — {payload.get('label', source_name)}. "
        f"Raw series retrieved {date.today()}; see source_url for the live data."
    )
    return [Chunk(
        text=summary,
        source_name=source_name,
        source_url=f"{base}?{requests.compat.urlencode(params or {})}",
        date=str(date.today()),
        source_type="api",
    )]


def load_verified_facts(path: str) -> list[Chunk]:
    """Load the pre-gathered, cited fact set in data/verified_facts_*.json as chunks —
    used so the pipeline has real grounded content to demo against without needing
    live internet access at run time. See that file's _note field."""
    data = json.loads(Path(path).read_text())
    chunks = []
    for fact in data["facts"]:
        chunks.append(Chunk(
            text=fact["statement"] + (f" Driver: {fact['driver']}" if fact.get("driver") else ""),
            source_name=fact["source_name"],
            source_url=fact["source_url"],
            date=fact["date"],
            source_type="verified_fact",
        ))
    return chunks


def save_chunks(chunks: list[Chunk], out_path: str):
    Path(out_path).write_text(json.dumps([asdict(c) for c in chunks], indent=2))


if __name__ == "__main__":
    demo_chunks = load_verified_facts("verified_facts_2026-08.json")
    print(f"Loaded {len(demo_chunks)} verified-fact chunks:")
    for c in demo_chunks:
        print(f"  [{c.date}] {c.source_name}: {c.text[:90]}...")
