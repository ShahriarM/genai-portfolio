"""Week 2 — Calling models from Python: structured summary of a DFAST disclosure, compared across two model sizes."""
import sys
import time
from pathlib import Path

import anthropic
import requests

BASE_URL = "http://localhost:8079"   # on the T480s: "http://localhost:8081"
MODELS = ["gemma-4-e4b-it", "qwen3-14b"]   # small vs. larger model on the local server
MAX_TOKENS = 4000                    # thinking plus a full structured summary
TIMEOUT = 600                        # larger models can take minutes, and the server may need to load them first

DOCUMENT = Path(__file__).parent / "pnc-2026.txt"   # PNC 2026 company-run DFAST disclosure

SYSTEM_PROMPT = "You are a model risk analyst at a bank. Summarize regulatory documents accurately and only from the text given."
INSTRUCTIONS = """Summarize the stress test disclosure below using exactly these headings:

1. Bank and test: who ran the test, the as-of date and the planning horizon
2. Scenario: the main assumptions of the severely adverse scenario
3. Key results: minimum capital ratios, total loan losses and the largest loss drivers, with numbers
4. Methodology: how losses, revenue and capital were projected
5. Governance: who reviews and approves the stress test

Use short bullet points and quote figures exactly as they appear."""

client = anthropic.Anthropic(base_url=BASE_URL, api_key="none", timeout=TIMEOUT)


def load_model(model):
    """Ask the server to load a model and wait until it is ready; the server swaps out the previous one."""
    requests.post(f"{BASE_URL}/models/load", json={"model": model}).raise_for_status()
    deadline = time.monotonic() + TIMEOUT
    while time.monotonic() < deadline:
        status = {m["id"]: m["status"]["value"] for m in requests.get(f"{BASE_URL}/models").json()["data"]}
        if status.get(model) == "loaded":
            return
        time.sleep(2)
    sys.exit(f"{model} did not finish loading within {TIMEOUT} seconds.")


document = DOCUMENT.read_text()
user_message = f"{INSTRUCTIONS}\n\n<document>\n{document}\n</document>"

results = []
for model in MODELS:
    print(f"\n{'=' * 70}\n{model}\n{'=' * 70}")
    load_model(model)                # loading time is kept out of the timing below
    start = time.perf_counter()
    try:
        msg = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.APITimeoutError:
        print(f"No reply within {TIMEOUT} seconds — skipping.")
        continue
    except anthropic.APIConnectionError:
        sys.exit(f"Could not reach the server at {BASE_URL} — is it running?")
    except anthropic.APIStatusError as e:
        print(f"Server error for {model}: {e.message} — skipping.")
        continue
    seconds = time.perf_counter() - start

    # the reply can start with a thinking block, so keep only the text blocks
    print("".join(b.text for b in msg.content if b.type == "text"))

    # the server caches repeated prompt text and counts it separately, so add it back
    input_tokens = msg.usage.input_tokens + (msg.usage.cache_read_input_tokens or 0)
    results.append((model, input_tokens, msg.usage.output_tokens, seconds, msg.stop_reason))

print(f"\n{'model':<20}{'input tok':>10}{'output tok':>12}{'seconds':>9}{'tok/s':>8}  stop reason")
for model, input_tokens, output_tokens, seconds, stop_reason in results:
    print(f"{model:<20}{input_tokens:>10}{output_tokens:>12}{seconds:>9.1f}{output_tokens / seconds:>8.1f}  {stop_reason}")
