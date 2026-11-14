"""Week 6 — Your first RAG app: answer questions from the model-risk documents, with citations."""
import streamlit as st

from rag import search

# TODO (step 1): build the prompt from the retrieved chunks and ask Claude to answer only from them,
#                citing the source of each claim
# TODO (step 2): make the model say "not found in the documents" when the chunks do not contain the answer
# TODO (step 3): this Streamlit page: a text box for the question, the answer, and the chunks that were used

st.title("Model risk document Q&A")
question = st.text_input("Ask a question about the documents")
if question:
    for hit in search(question):
        st.write(f"**{hit['source']}** (chunk {hit['chunk']}, similarity {hit['similarity']:.2f})")
        st.write(hit["text"][:300] + "...")
