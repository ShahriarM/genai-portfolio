"""Week 7 — the experiment grid. Changes one thing at a time from the Week 5 baseline
(500 tokens, overlap 80, k = 5) and prints a Markdown row per configuration for results.md.

    python experiments.py            # all three grids, about 5 minutes on CPU
"""
import time

from questions import QUESTIONS
from retrieval import BM25Index, VectorIndex, chunk, hit_rate, hybrid, load_documents

BASE = {"size": 500, "overlap": 80, "k": 5}
GRIDS = {                                   # one axis varies per grid, the others stay at BASE
    "Chunk size": [{"size": s} for s in (300, 500, 600, 1000)],
    "Overlap":    [{"overlap": o} for o in (0, 40, 80, 150)],
    "k":          [{"k": k} for k in (3, 5, 10, 20)],
}

docs = load_documents()
indexes = {}                                # (size, overlap) -> (chunks, vector index, bm25 index); built once


def get_indexes(size, overlap):
    if (size, overlap) not in indexes:
        t = time.monotonic()
        chunks = chunk(docs, size, overlap)
        indexes[(size, overlap)] = (chunks, VectorIndex(chunks), BM25Index(chunks))
        print(f"  built size={size} overlap={overlap}: {len(chunks)} chunks in {time.monotonic() - t:.0f} s")
    return indexes[(size, overlap)]


def row(size, overlap, k):
    chunks, vec, bm = get_indexes(size, overlap)
    searches = {
        "vector": vec.search,
        "bm25": bm.search,
        "hybrid": lambda q, k: hybrid(vec.search(q, 20), bm.search(q, 20), k=k),
    }
    out = []
    for name, fn in searches.items():
        n, per = hit_rate(fn, k)
        misses = ", ".join(str(i + 1) for i, ok in enumerate(per) if not ok) or "—"
        out.append(f"| {size} | {overlap} | {k} | {len(chunks)} | {name} | {n} | {misses} |")
    return out


if __name__ == "__main__":
    header = "| Chunk size | Overlap | k | Chunks | Search | Hits / 12 | Misses |\n|---|---|---|---|---|---|---|"
    for grid, settings in GRIDS.items():
        print(f"\n### {grid}\n\n{header}")
        for s in settings:
            cfg = BASE | s
            for line in row(cfg["size"], cfg["overlap"], cfg["k"]):
                print(line)
