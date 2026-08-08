"""
Local, offline embedding + retrieval — no paid embeddings API required.

Uses sentence-transformers/all-MiniLM-L6-v2: small, fast, free, runs on CPU.
Traded off deliberately against a larger/paid embedding model — see
docs/methodology.md "Known limitations" for the reasoning.
"""

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np


class LocalVectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.chunks: list[dict] = []
        self.embeddings: np.ndarray | None = None

    def add_chunks(self, chunks: list):
        """chunks: list of ingest.Chunk (or dicts with the same fields)"""
        as_dicts = [asdict(c) if not isinstance(c, dict) else c for c in chunks]
        texts = [c["text"] for c in as_dicts]
        new_embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

        self.chunks.extend(as_dicts)
        self.embeddings = (
            new_embeddings if self.embeddings is None
            else np.vstack([self.embeddings, new_embeddings])
        )

    def retrieve(self, query: str, k: int = 8) -> list[dict]:
        if self.embeddings is None or len(self.chunks) == 0:
            return []
        query_vec = self.model.encode([query], normalize_embeddings=True)[0]
        scores = self.embeddings @ query_vec  # cosine sim, since both are normalized
        top_idx = np.argsort(-scores)[:k]
        results = []
        for idx in top_idx:
            chunk = dict(self.chunks[idx])
            chunk["_similarity"] = round(float(scores[idx]), 4)
            results.append(chunk)
        return results

    def save(self, path: str):
        Path(path).write_text(json.dumps({
            "chunks": self.chunks,
            "embeddings": self.embeddings.tolist() if self.embeddings is not None else [],
        }))

    def load(self, path: str):
        data = json.loads(Path(path).read_text())
        self.chunks = data["chunks"]
        self.embeddings = np.array(data["embeddings"]) if data["embeddings"] else None


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from ingest import load_verified_facts

    store = LocalVectorStore()
    store.add_chunks(load_verified_facts("data/verified_facts_2026-08.json"))

    results = store.retrieve("has the ECB changed interest rates recently", k=3)
    print("Top matches for 'has the ECB changed interest rates recently':\n")
    for r in results:
        print(f"  [{r['_similarity']}] {r['source_name']}: {r['text'][:100]}...")
