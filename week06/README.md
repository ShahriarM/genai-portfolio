# Week 6 — Your first RAG app

Deliverable: `app.py`, a Streamlit app that answers questions about the model-risk documents with citations.

## Layout

| Path | Purpose |
|---|---|
| `rag.py` | Retrieval: `search(question, k=5)` over the Chroma index built in Week 5. Already working |
| `app.py` | The app. Starter only: shows the search results. Generation, citations and the "not found" rule are TODO |
| `test_questions.md` | The 15 test questions, with correct answers and the app's answers |

The index lives in `../week05/chroma_db/` and is not committed. If it is missing, run `week05/rag_search.ipynb` from the top to rebuild it. Run the app from this folder: `streamlit run app.py`.

## Steps (from the study plan)

1. Combine retrieval and generation: pass the top chunks to Claude with instructions to answer only from them and cite the source of each claim.
2. Make the model say "not found in the documents" when the context does not contain the answer.
3. Put a simple web interface on it with Streamlit (`pip install streamlit`).
4. Test with 15 questions you know the answers to, for example "What does SR 26-2 replace?"

## Known gap from Week 5

The SR 26-2 cover letter (`week05/docs/SR2602-letter.pdf`) was added to the corpus on 2026-11-14 and the index rebuilt (422 chunks). The letter says SR 26-2 supersedes SR 11-7 and SR 21-8, so the answer to question 1 is now in the index. Vector search still does not find it: for "What does SR 26-2 replace?" the letter's chunk ranks 45th of 422 (cosine similarity 0.13), because the letter is one 342-word chunk that is mostly addresses and boilerplate, and the two sentences that answer the question are a small part of it. Rephrasing the question ("Which SR letters does SR 26-2 supersede?") does not help.

So question 1 will still come back "not found in the documents" from a correct app, and that is the right behaviour given what retrieval returns. The fix is a retrieval change, which is Week 7's topic: smaller chunks, or keyword search (BM25) alongside vector search, which would match "SR 26-2" and "supersedes" directly. Keep question 1 in the test set as a known failure to measure against.
