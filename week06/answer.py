"""Week 6 — Your first RAG app: answer a question from the retrieved chunks, with citations.

Step 1 of the plan: retrieval (rag.search) plus generation. The model is told to answer only
from the passages it is given and to cite them. Run from this folder:

    python answer.py "What is effective challenge?"
"""
import sys
import time

import anthropic

from rag import search

BASE_URL = "http://localhost:8079"   # local llama.cpp server with an Anthropic-compatible endpoint
MODEL = "qwen3-14b"                  # must be the model loaded on the server
MAX_TOKENS = 2000                    # Qwen thinks before it answers, and the thinking counts against this
TIMEOUT = 180                        # seconds; 5 passages of 500 tokens take the server a while to read
NOT_FOUND = "Not found in the documents."

SYSTEM_PROMPT = """You answer questions for bank model-risk analysts using only the passages you are given.

Rules:
- Use only the passages. Do not use anything you know from elsewhere, even if you are sure of it.
- After every claim, cite the passage it came from as [1], [2], etc. A sentence may cite more than one passage.
- If the passages do not contain the answer, reply with exactly: Not found in the documents.
  Do not guess, and do not answer a different question that the passages do cover.
- Be brief: a few sentences, or a short list. Quote figures exactly as the passages give them."""

client = anthropic.Anthropic(base_url=BASE_URL, api_key="none", timeout=TIMEOUT)


def build_prompt(question, chunks):
    """The user message: the numbered passages, then the question."""
    passages = "\n\n".join(
        f'<passage id="{i}" source="{c["source"]}" chunk="{c["chunk"]}">\n{c["text"]}\n</passage>'
        for i, c in enumerate(chunks, start=1)
    )
    return f"{passages}\n\nQuestion: {question}"


def answer(question, k=5):
    """Retrieve k chunks, ask the model, and return the answer with the chunks it was given."""
    chunks = search(question, k)
    msg = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(question, chunks)}],
        extra_body={"temperature": 0},                                  # repeatable answers (Week 3)
    )
    text = "".join(b.text for b in msg.content if b.type == "text").strip()   # skip the thinking block
    return {
        "question": question,
        "answer": text,
        "not_found": text.startswith(NOT_FOUND.rstrip(".")),              # Step 2 flag, for the test table
        "chunks": chunks,                                                 # [1] is chunks[0], and so on
        "usage": {"input": msg.usage.input_tokens, "output": msg.usage.output_tokens},
    }


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What is effective challenge?"
    start = time.monotonic()
    try:
        result = answer(question)
    except anthropic.APIConnectionError:
        sys.exit(f"Could not reach the server at {BASE_URL} — is it running?")
    except anthropic.APITimeoutError:
        sys.exit(f"No reply within {TIMEOUT} seconds.")
    print(f"Q: {question}\n\n{result['answer']}\n")
    print("Passages:")
    for i, c in enumerate(result["chunks"], start=1):
        print(f"  [{i}] {c['source']} chunk {c['chunk']} (similarity {c['similarity']:.2f})")
    u = result["usage"]
    print(f"\nTokens in/out: {u['input']}/{u['output']}; {time.monotonic() - start:.0f} s")
