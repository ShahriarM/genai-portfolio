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

**3. Hybrid search is only as good as its merge.** The two searches miss different questions, so their union covers everything, but equal-weight reciprocal rank fusion at k = 5 scores no better than vector alone (8). Vector's confident wrong rankings outvote BM25's right ones. Hybrid only pays off when k is large enough to let both lists through: 10 at k = 10, and all 12 at k = 20. That is the best result in the table, bought with 10,000 tokens of context per question, four times the baseline, and the model then has to find the answer among 20 passages. Weighting BM25 above vector in the fusion was the obvious next experiment; it is in the section below, and it helped much less than expected.

**4. Chunk size and overlap matter less than the search type.** Across sizes 300–1,000, BM25 stays at 9–11 and vector at 7–8. Larger chunks help BM25 slightly (more words per chunk to match) and hurt vector slightly (the embedding model reads only the first 512 tokens, so a 1,000-token chunk is embedded from half its text). Overlap is noise at this scale: it changes which figure question happens to land in a chunk boundary, nothing more. The one exception is 300 tokens with hybrid (10 at k = 5), which is the same as hybrid at k = 10 with 500-token chunks: in both cases the model would see about 3,000–5,000 tokens, and it is the amount of text retrieved, not the chunk size, that is doing the work.

**What this means for the app.** The Week 6 app uses vector search at k = 5 and gets 8 of 12. Switching to BM25 alone gives 10 of 12 with no other change. Hybrid with k = 10 gives 10 as well, and k = 20 gives 12, at a cost in tokens and reading time. A weighted hybrid does not beat BM25 at k = 5 (see below). The right next step is re-running the Week 6 question set end to end with BM25 or hybrid retrieval, to see whether the model's answers improve as much as retrieval did.

## Weighted hybrid

Run on 2026-11-15 with `python weighted_hybrid.py`. `hybrid()` now takes a weight per list: each list votes `weight / (c + rank)`. The vector weight stays at 1.

### BM25 weight (500 tokens, overlap 80, c = 60, top 20 from each search)

| BM25 weight | k = 3 | k = 5 | k = 10 | Misses at k = 5 |
|---|---|---|---|---|
| 0.5 | 7 | 7 | 8 | 1, 2, 3, 4, 12 |
| 1 (equal) | 8 | 8 | 10 | 2, 3, 4, 12 |
| 1.5 | 8 | 9 | 10 | 2, 3, 12 |
| 2 | 8 | 9 | 10 | 2, 3, 12 |
| 3 | 8 | 9 | 10 | 2, 3, 12 |
| 5 | 8 | 9 | 11 | 2, 3, 12 |
| 10 | 8 | 9 | 11 | 2, 3, 12 |

### Other settings (BM25 weight 2, k = 5)

| Setting | Values | Hits / 12 |
|---|---|---|
| Fusion constant c | 1 / 10 / 60 / 200 | 10 / 9 / 9 / 9 |
| Depth (hits taken from each search) | 5 / 10 / 20 / 50 | 10 / 9 / 9 / 9 |

### Other chunk sizes (k = 5, c = 60, depth 20)

| Chunk size | Equal weight | BM25 weight 2 | BM25 weight 3 | BM25 alone |
|---|---|---|---|---|
| 300 | 10 | 10 | 10 | 9 |
| 500 | 8 | 9 | 9 | 10 |
| 1,000 | 8 | 9 | 9 | 11 |

### Where the right chunk ranks (500 tokens, overlap 80, of 422 chunks)

| Question | Vector | BM25 | Hybrid, equal | Hybrid, BM25 × 2 |
|---|---|---|---|---|
| 1 SR 26-2 replaces | 45 | 1 | 2 | 1 |
| 2 definition of "model" | 3 | 69 | 8 | 23 |
| 3 effective challenge (SR 26-2) | 39 | 10 | 20 | 10 |
| 4 SR 11-7 date and agencies | 155 | 4 | 7 | 4 |
| 5 three core elements | 2 | 3 | 1 | 1 |
| 6 OCC booklet audience | 5 | 1 | 3 | 1 |
| 7 unemployment peak | 1 | 1 | 1 | 1 |
| 8 equity prices | 1 | 2 | 2 | 2 |
| 9 real GDP | 2 | 3 | 1 | 1 |
| 10 PNC CET1 | 5 | 1 | 2 | 2 |
| 11 Wells Fargo CET1 | 2 | 1 | 1 | 1 |
| 12 JPMorgan CET1 | 23 | 3 | 12 | 12 |

### What it shows

**Weighting did not do what I expected.** Before running this, the write-up above predicted a BM25-weighted fusion would reach 11–12 at k = 5. It reaches 9, one better than equal weights and one *worse* than BM25 alone (10). Any weight from 1.5 to 10 gives the same 9, so the result is not a matter of picking the wrong number.

**The rank table explains why.** Rank fusion rewards *agreement*. A chunk that both searches rank moderately well collects two votes and outscores a chunk that one search ranks very well and the other does not rank at all. Question 12 shows it: BM25 puts the right chunk 3rd, vector search puts it 23rd (outside the top 20, so no vote), and the fused list puts it 12th, behind chunks that both searches found mildly relevant. Raising the BM25 weight does not change that, because the competing chunks have BM25 votes too. Question 2 is the mirror image: vector 3rd, BM25 69th, and the more BM25 is weighted the further it falls (8th to 23rd).

So fusion helps where the searches roughly agree (questions 5 and 9 go to rank 1) and hurts exactly where one search is right and the other is blind, which are the questions hybrid search was supposed to rescue. For those, the union of the two lists has the answer, and the only reliable way to keep it is to retrieve more: hybrid reaches 10–11 at k = 10 and 12 at k = 20.

**The settings that reach 10 at k = 5 are not real improvements.** c = 1 and depth = 5 both score 10, but both work by making the fusion behave more like "take the top few from each list", and each is one question better on a 12-question set. I would not ship either on this evidence. The same goes for the 300-token row, where hybrid beats BM25 by one.

**Limits.** These settings were tuned and scored on the same 12 questions, so even the differences that look consistent are optimistic. The questions also lean towards named documents and exact figures, which favours BM25. A corpus of looser, more conceptual questions could reverse the ranking of the two searches.

**Conclusion for the app.** At k = 5, BM25 alone is the best single change (8 to 10). Hybrid is worth it only with k of 10 or more, where it is as good as or better than either search. Fixing question 3 properly needs a different idea from the contextual-retrieval write-up: put the document's name into each chunk before indexing, so the effective-challenge chunk says "SR 26-2" somewhere.

