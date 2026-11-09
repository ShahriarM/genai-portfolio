# Week 5 — RAG basics

Deliverable: an indexed corpus of public model-risk documents and a working `search(question)` function that returns the 5 most similar chunks with their source file names.

## Layout

| Path | Purpose |
|---|---|
| `docs/` | New source documents for this week (PDF), with a README on each one |
| `chroma_db/` | The local Chroma vector database. Rebuilt from the documents, so it is not committed |
| `rag_search.ipynb` | The deliverable notebook: load, chunk, embed, store, search |

## Corpus (12 documents)

Existing files, used where they are:

| File | Notes |
|---|---|
| `../week04/docs/SR2602a1.pdf` | SR 26-2 guidance, the current model risk guidance |
| `../week04/docs/OCC-model-risk-booklet-2021.pdf` | OCC booklet, rescinded, third-party copy |
| `../week02/pnc-2026.pdf` | PNC 2026 stress test disclosure |

Nine new documents are in `docs/`: SR 11-7 and its cover letter, three Federal Reserve stress test documents, and four banks' 2026 stress test disclosures. See `docs/README.md` for details and sources.

## Steps (from the study plan)

1. Collect 10–20 public documents on model risk and convert the PDFs to text with `pypdf`.
2. Split the text into chunks of roughly 500–800 tokens with some overlap.
3. Embed the chunks (Week 4 code) and store them in Chroma (`pip install chromadb`).
4. Write `search(question)` that returns the 5 most similar chunks with their source file names.
