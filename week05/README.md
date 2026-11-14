# Week 5 — RAG basics

Deliverable: an indexed corpus of public model-risk documents and a working `search(question)` function that returns the 5 most similar chunks with their source file names.

## Layout

| Path | Purpose |
|---|---|
| `docs/` | New source documents for this week (PDF), with a README on each one |
| `chroma_db/` | The local Chroma vector database. Rebuilt from the documents, so it is not committed |
| `rag_search.ipynb` | The deliverable notebook: load, chunk, embed, store, search |

## Corpus (13 documents)

Existing files, used where they are:

| File | Notes |
|---|---|
| `../week04/docs/SR2602a1.pdf` | SR 26-2 guidance, the current model risk guidance |
| `../week04/docs/OCC-model-risk-booklet-2021.pdf` | OCC booklet, rescinded, third-party copy |
| `../week02/pnc-2026.pdf` | PNC 2026 stress test disclosure |

Ten new documents are in `docs/`: SR 11-7 and its cover letter, the SR 26-2 cover letter, three Federal Reserve stress test documents, and four banks' 2026 stress test disclosures. See `docs/README.md` for details and sources.

## Steps (from the study plan)

1. Collect 10–20 public documents on model risk and convert the PDFs to text with `pypdf`.
2. Split the text into chunks of roughly 500–800 tokens with some overlap.
3. Embed the chunks (Week 4 code) and store them in Chroma (`pip install chromadb`).
4. Write `search(question)` that returns the 5 most similar chunks with their source file names.

## Findings

- **The index covers 13 documents in 422 chunks** of 500 tokens with an 80-token overlap, embedded with `all-MiniLM-L6-v2` at its 512-token limit. Table-of-contents dot leaders had to be stripped first: before that, the OCC booklet's contents pages were the top hit for almost any question.
- **Search returns similar text, not answers.** "What is effective challenge?" returns the OCC booklet and SR 11-7 passages that use the term; the reader still has to find the definition in them. It always returns 5 chunks, even when nothing fits.
- **SR 26-2 and the question "What does SR 26-2 replace?"** The guidance (`SR2602a1.pdf`) does not say what it replaces; only the cover letter does. The letter was added as `docs/SR2602-letter.pdf` on 2026-11-14. Its single 342-word chunk ends with "Supersedes: SR letter 11-7 … SR letter 21-8 …", yet for that question it ranks 45th of 422 chunks (cosine similarity 0.13; the top hit is an unrelated Fed scenario chunk at 0.22). Rephrasing does not help (40th and 80th). The chunk is mostly letterhead and distribution boilerplate, so the two answering sentences carry little weight in the averaged vector. Having the answer in the corpus is not the same as being able to retrieve it.
- **Similarities are low across the board**, 0.2–0.6 for good matches, so no fixed cutoff separates hits from misses with this model. Week 7 (smaller chunks, BM25 keyword search alongside vector search) is where to fix both this and the SR 26-2 case.

