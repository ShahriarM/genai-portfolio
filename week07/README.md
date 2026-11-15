# Week 7 — Better retrieval

Deliverable: `results.md`, a table of retrieval hit rates per configuration, treated like a model comparison.

## Layout

| Path | Purpose |
|---|---|
| `questions.py` | The scoring set: the 12 answerable questions from Week 6, each with a regex for the phrase that answers it |
| `retrieval.py` | Building blocks: document loading and chunking (Week 5 code with the size as a parameter), `VectorIndex`, `BM25Index`, `hybrid()` (reciprocal rank fusion), `hit_rate()`. Running it scores the Week 5 configuration |
| `experiments.py` | The experiment grid: chunk size × overlap × k × search type. TODO |
| `results.md` | The comparison table and what it shows |

## How a configuration is scored

A question counts as a **hit** when any of the k retrieved chunks comes from the right file and contains the evidence phrase (for example `peak of 10 percent in the third quarter of 2027`). This is independent of chunk size, so configurations can be compared. It measures retrieval only: whether the model then answers correctly was Week 6's question.

The three out-of-corpus questions from Week 6 are excluded, since no chunk is right for them.

## Steps (from the study plan)

1. Read Anthropic's write-up on contextual retrieval to see why plain chunking misses answers.
2. Run experiments, changing one thing at a time: chunk size (300 / 600 / 1,000 tokens), overlap, and the number of chunks retrieved.
3. Add keyword search (BM25, via `rank_bm25`) alongside vector search and merge the results (hybrid search).
4. For each setting, record how many of the 12 test questions retrieve the right chunk.

## Notes

- Indexes are built in memory with NumPy, not in Chroma: each experiment needs a fresh index, and at a few hundred chunks a full dot product is instant. Chroma stays the store for the app.
- `all-MiniLM-L6-v2` reads at most 512 tokens. A 1,000-token chunk is embedded from its first 512 tokens only; BM25 sees all of it. Expect that to show in the results.
- Building a vector index takes about 30 s per configuration on CPU (embedding); BM25 is instant.
