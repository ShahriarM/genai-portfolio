# Week 2 — Calling models from Python

## What's here

| File | What it does |
|---|---|
| `chat.py` | Sends a system prompt and a user message, streams the reply, prints input/output token counts, and handles rate-limit, timeout and connection errors. |
| `chat_interactive.py` | The same in a loop: a terminal chat that keeps the conversation history. |
| `summarize.py` | Loads a stress test disclosure, asks for a structured five-section summary, and compares two model sizes. |
| `pnc-2026.pdf` / `.txt` | Input document: PNC's 2026 Dodd-Frank Act company-run stress test disclosure (11 pages, about 3,200 words). |

## Setup

All scripts call a local `llama-server` (llama.cpp) through its Anthropic-compatible endpoint at `http://localhost:8079`, using the official `anthropic` Python SDK with `base_url` pointed at the server. Moving to the hosted Claude API only means changing `base_url`, the API key and the model name.

## Cost per run: `summarize.py`

Same prompt and document, run on 2026-10-30. Times exclude model loading.

| Model | Size | Input tokens | Output tokens | Time | Speed |
|---|---|---|---|---|---|
| `gemma-4-e4b-it` | ~4B | 4,925 | 2,198 | 56 s | 39 tok/s |
| `qwen3-14b` | 14B | 4,854 | 1,721 | 79 s | 22 tok/s |

Running locally, the money cost per run is effectively zero; the real cost is time and GPU memory (the server only holds one of these models at a time). Output tokens include the model's hidden reasoning, which is why a summary of about 600 words used around 2,000 output tokens. On a paid API that reasoning is billed, so it matters for cost.

## Accuracy check

I checked the figures in each summary against the source text.

- **qwen3-14b:** every figure checked was correct, and it was the more complete summary (PPNR of $16.9B, the full loan-loss breakdown, Treasury and mortgage-spread paths).
- **gemma-4-e4b-it, run 1:** gave the commercial real estate loss ($2.9B, 24%) as residential real estate (actually $1.4B, 12%), and left commercial real estate out.
- **gemma-4-e4b-it, run 2:** loan losses correct but incomplete (dropped residential and consumer losses), plus a formatting error ("$50% or $6.1 billion").

**Takeaway:** the larger model was about 40% slower but more accurate and complete. The smaller model's output looked equally confident when it was wrong, and it changed between runs on identical input. A summary needs checking against the source before anyone relies on it. Week 3's stability test measures that run-to-run variation.

## What broke

- **Thinking blocks:** `msg.content[0].text` crashed because Gemma returns a thinking block before the answer. Fix: keep only blocks with `type == "text"`, or use `stream.text_stream`.
- **`max_tokens` too low:** at 500 the answer was cut off, because reasoning counts toward the limit.
- **Model not loaded:** the server doesn't load models on request, so the call failed with `model is not loaded`. `summarize.py` now loads each model through `/models/load` and waits until it's ready. Loading one model unloads the other, so reload Gemma before running `chat.py`.
- **Token counts:** the server counts repeated prompt text separately as `cache_read_input_tokens`, so `input_tokens` alone looked too small. `summarize.py` adds the two together.
- **SDK change:** the installed `anthropic` SDK (1.15.0) no longer accepts `temperature`. It has to be sent through `extra_body` (needed in Week 3).
