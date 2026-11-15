"""Week 7 — Better retrieval: the building blocks for the experiments.

- load_documents():               text of the 13 PDFs (same list and cleaning as Week 5)
- chunk(docs, size, overlap):     token-window chunks, like Week 5 but with the size as a parameter
- VectorIndex / BM25Index:        the two kinds of search, same interface: .search(question, k) -> chunks
- hybrid(vector_hits, bm25_hits): merge two ranked lists with reciprocal rank fusion
- hit_rate(search_fn, k):         how many of the 12 questions get a chunk containing the evidence

Indexes are kept in memory with NumPy rather than in Chroma: each experiment builds a fresh index,
and at a few hundred chunks a dot product over all of them is instant.
"""
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
from pypdf import PdfReader
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

from questions import QUESTIONS

ROOT = Path(__file__).resolve().parent.parent
PDFS = sorted((ROOT / "week05" / "docs").glob("*.pdf")) + [
    ROOT / "week04" / "docs" / "SR2602a1.pdf",
    ROOT / "week04" / "docs" / "OCC-model-risk-booklet-2021.pdf",
    ROOT / "week02" / "pnc-2026.pdf",
]

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2", model_max_length=10**7)
model = SentenceTransformer("all-MiniLM-L6-v2")
model.max_seq_length = 512          # the most this model reads; chunks longer than this are cut off when embedded


@lru_cache(maxsize=1)
def load_documents():
    """{file name: cleaned text}. Cached, because reading the PDFs takes ~20 s."""
    docs = {}
    for p in PDFS:
        pages = [page.extract_text() or "" for page in PdfReader(p).pages]
        text = re.sub(r"(\. ?){4,}", " ", " ".join(pages))     # table-of-contents dot leaders
        docs[p.name] = re.sub(r"\s+", " ", text).strip()
    return docs


def chunk(docs, size, overlap):
    """Token windows of `size` tokens starting `size - overlap` apart. Returns a list of dicts."""
    out = []
    for name, text in docs.items():
        offsets = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]
        step = size - overlap
        for n, start in enumerate(range(0, len(offsets), step)):
            end = min(start + size, len(offsets))
            out.append({"source": name, "chunk": n, "text": text[offsets[start][0]:offsets[end - 1][1]]})
            if end == len(offsets):
                break
    return out


class VectorIndex:
    """Cosine search over normalized embeddings, same model as Week 5."""

    def __init__(self, chunks):
        self.chunks = chunks
        self.emb = model.encode([c["text"] for c in chunks], batch_size=16, normalize_embeddings=True)

    def search(self, question, k):
        q = model.encode([question], normalize_embeddings=True)[0]
        scores = self.emb @ q
        return [self.chunks[i] | {"score": float(scores[i])} for i in np.argsort(-scores)[:k]]


def _tokens(text):
    return re.findall(r"[a-z0-9][a-z0-9.\-]*", text.lower())      # keeps "26-2", "11-7", "9.6%"-style tokens together


class BM25Index:
    """Keyword search: exact words matter, meaning does not."""

    def __init__(self, chunks):
        self.chunks = chunks
        self.bm25 = BM25Okapi([_tokens(c["text"]) for c in chunks])

    def search(self, question, k):
        scores = self.bm25.get_scores(_tokens(question))
        return [self.chunks[i] | {"score": float(scores[i])} for i in np.argsort(-scores)[:k]]


def hybrid(*ranked_lists, k, c=60):
    """Reciprocal rank fusion: each list votes 1/(c + rank) for its chunks; the top k by total win."""
    votes = {}
    for hits in ranked_lists:
        for rank, h in enumerate(hits, start=1):
            key = (h["source"], h["chunk"])
            votes.setdefault(key, [0.0, h])
            votes[key][0] += 1 / (c + rank)
    merged = sorted(votes.values(), key=lambda v: -v[0])[:k]
    return [h | {"score": s} for s, h in merged]


def hit_rate(search_fn, k):
    """search_fn(question, k) -> chunks. Returns (hits, [per-question True/False])."""
    results = []
    for question, source, evidence in QUESTIONS:
        hits = search_fn(question, k)
        results.append(any(h["source"] == source and re.search(evidence, h["text"]) for h in hits))
    return sum(results), results


def check_evidence():
    """Sanity check: every evidence regex must match its document's text, or the question can never hit."""
    docs = load_documents()
    for q, source, evidence in QUESTIONS:
        assert re.search(evidence, docs[source]), f"evidence not found for: {q}"
    print("all", len(QUESTIONS), "evidence phrases found")


if __name__ == "__main__":
    check_evidence()
    chunks = chunk(load_documents(), size=500, overlap=80)       # the Week 5 configuration
    print(len(chunks), "chunks")
    vec, bm = VectorIndex(chunks), BM25Index(chunks)
    for name, fn in [("vector", vec.search), ("bm25", bm.search),
                     ("hybrid", lambda q, k: hybrid(vec.search(q, 20), bm.search(q, 20), k=k))]:
        n, per = hit_rate(fn, k=5)
        print(f"{name:7s} k=5: {n}/{len(QUESTIONS)}  misses: {[i+1 for i, ok in enumerate(per) if not ok]}")
