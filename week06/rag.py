"""Week 6 — retrieval for the RAG app: search the Chroma index built in Week 5."""
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

DB_PATH = Path(__file__).resolve().parent.parent / "week05" / "chroma_db"   # built by week05/rag_search.ipynb
COLLECTION = "model_risk"

# The index was built with this model at this length; questions must be embedded the same way
model = SentenceTransformer("all-MiniLM-L6-v2")
model.max_seq_length = 512
collection = chromadb.PersistentClient(path=str(DB_PATH), settings=Settings(anonymized_telemetry=False)).get_collection(COLLECTION)


def search(question, k=5):
    """The k chunks most similar to the question: dicts with source, chunk, similarity and text."""
    q = model.encode([question], normalize_embeddings=True)
    r = collection.query(query_embeddings=q.tolist(), n_results=k)
    return [
        {"source": m["source"], "chunk": m["chunk"], "similarity": 1 - d, "text": t}
        for m, d, t in zip(r["metadatas"][0], r["distances"][0], r["documents"][0])
    ]
