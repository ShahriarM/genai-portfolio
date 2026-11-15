"""Week 6 — Your first RAG app: a Streamlit page that answers questions from the model-risk documents, with citations.

Run from this folder:  streamlit run app.py
"""
import anthropic
import streamlit as st

from answer import BASE_URL, MODEL, answer

st.set_page_config(page_title="Model risk Q&A", layout="wide")
st.title("Model risk document Q&A")
st.caption(f"Answers come only from the indexed documents; each claim cites a passage. Model: {MODEL} on the local server.")

question = st.text_input("Ask a question about the documents", placeholder="What is effective challenge?")
k = st.sidebar.slider("Passages to retrieve", min_value=3, max_value=10, value=5)
st.sidebar.markdown("Passages are the 500-token chunks indexed in Week 5. The model sees only these.")

if question:
    with st.spinner("Retrieving passages and asking the model..."):
        try:
            result = answer(question, k)
        except anthropic.APIConnectionError:
            st.error(f"Could not reach the server at {BASE_URL}. Is llama-server running with {MODEL} loaded?")
            st.stop()
        except anthropic.APITimeoutError:
            st.error("The server did not reply in time. Try again, or ask a shorter question.")
            st.stop()

    st.subheader("Answer")
    if result["not_found"]:
        st.warning(result["answer"])                       # the "not found" case stands out from a real answer
    else:
        st.markdown(result["answer"])

    st.subheader("Passages the model was given")
    st.markdown("Citations like [2] refer to these numbers.")
    for i, c in enumerate(result["chunks"], start=1):
        with st.expander(f"[{i}] {c['source']} — chunk {c['chunk']} (similarity {c['similarity']:.2f})"):
            st.write(c["text"])

    u = result["usage"]
    st.caption(f"Tokens in/out: {u['input']}/{u['output']}")
