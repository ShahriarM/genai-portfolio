"""Week 7 — weighted hybrid search: does giving BM25 more say than vector search fix the merge?

Varies the BM25 weight (vector weight fixed at 1), the fusion constant c, and how many hits each
search contributes (depth), then checks the best setting on other chunk sizes.

    python weighted_hybrid.py        # about 3 minutes on CPU
"""
from retrieval import BM25Index, VectorIndex, chunk, hit_rate, hybrid, load_documents

docs = load_documents()


def build(size, overlap=80):
    chunks = chunk(docs, size, overlap)
    return VectorIndex(chunks), BM25Index(chunks)


def score(vec, bm, k, w_bm25, c=60, depth=20):
    fn = lambda q, k: hybrid(vec.search(q, depth), bm.search(q, depth), k=k, c=c, weights=[1.0, w_bm25])
    n, per = hit_rate(fn, k)
    return n, ", ".join(str(i + 1) for i, ok in enumerate(per) if not ok) or "—"


if __name__ == "__main__":
    vec, bm = build(500)

    print("### BM25 weight (500 tokens, overlap 80, c = 60, depth 20)\n")
    print("| BM25 weight | k = 3 | k = 5 | k = 10 | Misses at k = 5 |\n|---|---|---|---|---|")
    for w in (0.5, 1, 1.5, 2, 3, 5, 10):
        r = {k: score(vec, bm, k, w) for k in (3, 5, 10)}
        print(f"| {w} | {r[3][0]} | {r[5][0]} | {r[10][0]} | {r[5][1]} |")

    print("\n### Fusion constant c (BM25 weight 2, k = 5, depth 20)\n")
    print("| c | Hits / 12 | Misses |\n|---|---|---|")
    for c in (1, 10, 60, 200):
        n, m = score(vec, bm, 5, 2, c=c)
        print(f"| {c} | {n} | {m} |")

    print("\n### Depth: hits taken from each search before merging (BM25 weight 2, k = 5, c = 60)\n")
    print("| Depth | Hits / 12 | Misses |\n|---|---|---|")
    for d in (5, 10, 20, 50):
        n, m = score(vec, bm, 5, 2, depth=d)
        print(f"| {d} | {n} | {m} |")

    print("\n### Other chunk sizes (k = 5, c = 60, depth 20)\n")
    print("| Chunk size | Equal weight | BM25 weight 2 | BM25 weight 3 | BM25 alone |\n|---|---|---|---|---|")
    for size in (300, 500, 1000):
        v, b = (vec, bm) if size == 500 else build(size)
        print(f"| {size} | {score(v, b, 5, 1)[0]} | {score(v, b, 5, 2)[0]} | {score(v, b, 5, 3)[0]} | {hit_rate(b.search, 5)[0]} |")
