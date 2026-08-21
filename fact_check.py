"""
Independent grounding check: does every factual claim in a generated draft actually
appear in the chunks that were retrieved for it?

Deliberately blunt (regex-based numeric/date extraction + substring match), not a full
NLI grounding classifier. Treat the output as a useful flag for a human reviewer, not a
certification.
"""

import re


NUMBER_PATTERN = re.compile(r"-?\d+\.?\d*%?")


def extract_claims(draft_text: str) -> list[str]:
    """Pull out numeric tokens (rates, percentages, dates, counts) as the checkable
    claims — the cheapest reliable proxy for 'a fact that could be wrong'."""
    cleaned = re.sub(r"\[DATA SOURCE NOT CONNECTED:.*?\]", "", draft_text)
    # strip our own inline citation parentheticals, e.g. "(Source: ECB, 2026-06-11)" —
    # these are provenance metadata, not separate factual claims, and their hyphenated
    # dates would otherwise be misparsed into spurious fragments like "-06"
    cleaned = re.sub(r"\(Source:[^)]*\)", "", cleaned)
    # also strip trailing "Sources: A; B; C." citation-list lines
    cleaned = re.sub(r"Sources?:\s*[^\n]*", "", cleaned)
    return sorted(set(NUMBER_PATTERN.findall(cleaned)))


def is_grounded(claim: str, chunks: list[dict]) -> tuple[bool, str | None]:
    """A numeric claim is 'grounded' if the exact token appears in at least one chunk's
    text. Returns (is_grounded, matching_source_name_or_None)."""
    for chunk in chunks:
        if claim in chunk["text"]:
            return True, chunk["source_name"]
    return False, None


def check_draft(draft_text: str, retrieved_chunks: list[dict]) -> dict:
    claims = extract_claims(draft_text)
    results = []
    for claim in claims:
        grounded, source = is_grounded(claim, retrieved_chunks)
        results.append({"claim": claim, "grounded": grounded, "source": source})

    n_grounded = sum(1 for r in results if r["grounded"])
    coverage = round(n_grounded / len(results), 3) if results else 1.0
    unverified = [r["claim"] for r in results if not r["grounded"]]
    placeholders_used = len(re.findall(r"\[DATA SOURCE NOT CONNECTED:", draft_text))

    return {
        "n_claims_checked": len(results),
        "n_grounded": n_grounded,
        "coverage_score": coverage,
        "unverified_claims": unverified,
        "placeholders_used": placeholders_used,
        "detail": results,
        "verdict": (
            "PASS — all numeric claims traced to a source" if coverage == 1.0
            else f"REVIEW NEEDED — {len(unverified)} claim(s) not found in retrieved sources"
        ),
    }


if __name__ == "__main__":
    demo_draft = (
        "European data center vacancy fell below 10% in late 2024 and is forecast to "
        "reach 6.5% by end-2026 (Source: CBRE, 2026-01-01). Rents rose 6% in Berlin last year."
    )
    demo_chunks = [{
        "source_name": "CBRE",
        "text": "vacancy fell below 10% for the first time in late 2024, forecast to reach 6.5% by the close of 2026",
    }]
    result = check_draft(demo_draft, demo_chunks)
    print(f"Verdict: {result['verdict']}")
    print(f"Coverage: {result['coverage_score']}")
    if result["unverified_claims"]:
        print(f"Unverified: {result['unverified_claims']}")
