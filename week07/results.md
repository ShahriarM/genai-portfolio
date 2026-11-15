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

TODO: one row per configuration, changing one thing at a time.

| Chunk size | Overlap | k | Search | Hits / 12 | Misses |
|---|---|---|---|---|---|
| 500 | 80 | 5 | vector | 8 | 1, 3, 4, 12 |
| | | | | | |

## What the table shows

TODO
