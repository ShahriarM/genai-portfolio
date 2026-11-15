# Week 7 — Retrieval results

Scoring set: 12 questions (`questions.py`). Hit = a retrieved chunk from the right file contains the evidence phrase. Embedding model `all-MiniLM-L6-v2`; BM25 via `rank_bm25`; hybrid = reciprocal rank fusion of the top 20 from each.

## Baseline: the Week 5 configuration (500 tokens, overlap 80, k = 5)

| Search | Hits / 12 | Misses (question #) |
|---|---|---|
| Vector | 8 | 1, 3, 4, 12 |
| BM25 | 10 | 2, 3 |
| Hybrid (RRF, equal weight) | 8 | 2, 3, 4, 12 |

Run on 2026-11-15 with `python retrieval.py`. The vector misses match Week 6: questions 1 and 3 (the SR 26-2 letter and the effective-challenge chunk) and 12 (the JPMorgan holding-company table). Question 4 counts as a miss here because the evidence is the SR 11-7 title page; in Week 6 the model answered the date from the SR 26-2 letter instead.

## Experiments

Run on 2026-11-15 with `python experiments.py`: one axis changes per grid, the others stay at the baseline (500 tokens, overlap 80, k = 5). Building a vector index took 23–58 s per configuration on CPU.

### Chunk size (overlap 80, k = 5)

| Chunk size | Chunks | Vector | BM25 | Hybrid | Vector misses | BM25 misses | Hybrid misses |
|---|---|---|---|---|---|---|---|
| 300 | 800 | 7 | 9 | **10** | 1, 3, 4, 6, 9 | 2, 3, 4 | 2, 4 |
| 500 | 422 | 8 | 10 | 8 | 1, 3, 4, 12 | 2, 3 | 2, 3, 4, 12 |
| 600 | 343 | 8 | 10 | 9 | 1, 2, 3, 4 | 2, 3 | 2, 3, 4 |
| 1,000 | 196 | 7 | **11** | 8 | 1, 2, 3, 4, 9 | 3 | 2, 3, 4, 9 |

### Overlap (500 tokens, k = 5)

| Overlap | Chunks | Vector | BM25 | Hybrid | Vector misses | BM25 misses | Hybrid misses |
|---|---|---|---|---|---|---|---|
| 0 | 356 | 7 | 10 | 9 | 1, 2, 3, 4, 9 | 2, 3 | 2, 3, 4 |
| 40 | 387 | 7 | 9 | 9 | 1, 2, 3, 4, 9 | 2, 3, 5 | 2, 3, 4 |
| 80 | 422 | 8 | 10 | 8 | 1, 3, 4, 12 | 2, 3 | 2, 3, 4, 12 |
| 150 | 502 | 6 | 10 | **10** | 1, 2, 3, 4, 9, 12 | 2, 3 | 2, 4 |

### Number of chunks retrieved, k (500 tokens, overlap 80)

| k | Tokens sent to the model | Vector | BM25 | Hybrid | Vector misses | BM25 misses | Hybrid misses |
|---|---|---|---|---|---|---|---|
| 3 | ~1,500 | 6 | 9 | 8 | 1, 3, 4, 6, 10, 12 | 2, 3, 4 | 2, 3, 4, 12 |
| 5 | ~2,500 | 8 | 10 | 8 | 1, 3, 4, 12 | 2, 3 | 2, 3, 4, 12 |
| 10 | ~5,000 | 8 | 11 | 10 | 1, 3, 4, 12 | 2 | 3, 12 |
| 20 | ~10,000 | 8 | 11 | **12** | 1, 3, 4, 12 | 2 | — |

## What the table shows

**First, the caveat.** Twelve questions means one question is 8 percentage points. A difference of one hit between two rows is noise; only patterns that hold across several rows are worth believing. Two such patterns stand out, and both are about *which* questions miss rather than how many.

**1. Vector search has a blind spot for named documents, and no setting fixes it.** Questions 1, 3 and 4 ask about SR 26-2 or SR 11-7 by name. Vector search misses all three in every one of the 16 configurations, including k = 20: the right chunks rank 23rd to 45th. The embedding captures what a passage is *about* (model risk, validation) and not which document it is, so "SR 26-2" in the question carries almost no weight. Chunk size and overlap move the vector score between 6 and 8, but only by trading the figure questions (6, 9, 12) in and out; the named-document questions never come back.

**2. BM25 has the opposite blind spot.** Keyword search finds the named documents at once ("SR", "26-2", "11-7" are literal tokens) and scores 9–11 everywhere. It reliably misses question 2, "How does SR 26-2 define the term model?": the words "define", "term" and "model" appear in nearly every chunk, so they don't discriminate, and vector search gets this one easily. And it misses question 3 until k = 10, for the reason the contextual-retrieval write-up gives: the chunk that defines effective challenge never says "SR 26-2". The chunk has lost its context; only a chunk that carried its document's name would match.

**3. Hybrid search is only as good as its merge.** The two searches miss different questions, so their union covers everything, but equal-weight reciprocal rank fusion at k = 5 scores no better than vector alone (8). Vector's confident wrong rankings outvote BM25's right ones. Hybrid only pays off when k is large enough to let both lists through: 10 at k = 10, and all 12 at k = 20. That is the best result in the table, bought with 10,000 tokens of context per question, four times the baseline, and the model then has to find the answer among 20 passages. The next experiment is weighting BM25 above vector in the fusion, which the figures above suggest would reach 11–12 at k = 5.

**4. Chunk size and overlap matter less than the search type.** Across sizes 300–1,000, BM25 stays at 9–11 and vector at 7–8. Larger chunks help BM25 slightly (more words per chunk to match) and hurt vector slightly (the embedding model reads only the first 512 tokens, so a 1,000-token chunk is embedded from half its text). Overlap is noise at this scale: it changes which figure question happens to land in a chunk boundary, nothing more. The one exception is 300 tokens with hybrid (10 at k = 5), which is the same as hybrid at k = 10 with 500-token chunks: in both cases the model would see about 3,000–5,000 tokens, and it is the amount of text retrieved, not the chunk size, that is doing the work.

**What this means for the app.** The Week 6 app uses vector search at k = 5 and gets 8 of 12. Switching to BM25 alone gives 10 of 12 with no other change. Hybrid with k = 10 gives 10 as well, and k = 20 gives 12, at a cost in tokens and reading time. The right next step is a weighted hybrid at k = 5–10, then re-running the Week 6 question set end to end to see whether the model's answers improve as much as retrieval did.
