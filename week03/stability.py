"""Week 3 — Prompting properly: stability test. Same prompt N times at each temperature, then measure how much the answers vary."""
import json
import sys
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

import anthropic

BASE_URL = "http://localhost:8079"   # on the T480s: "http://localhost:8081"
MODEL = "gemma-4-e4b-it"             # must be the model loaded on the server
MAX_TOKENS = 3000                    # leaves room for the model's thinking plus the answer
TIMEOUT = 300
RUNS = 10
TEMPERATURES = [1.0, 0.0]            # 1.0 is the server default

SYSTEM_PROMPT = "You are a concise assistant who explains ideas to bank risk analysts."
PROMPT = "In one sentence, what is the single biggest risk of using a large language model to summarize loan documents?"

RESULTS = Path(__file__).parent / "stability_results.json"

client = anthropic.Anthropic(base_url=BASE_URL, api_key="none", timeout=TIMEOUT)


def ask(temperature):
    msg = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": PROMPT}],
        extra_body={"temperature": temperature},   # the SDK has no temperature argument any more
    )
    # the reply can start with a thinking block, so keep only the text blocks
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def similarity(answers):
    """Mean pairwise text similarity: 1.0 means every answer is identical."""
    pairs = list(combinations(answers, 2))
    return sum(SequenceMatcher(None, a, b).ratio() for a, b in pairs) / len(pairs)


results = {}
for temperature in TEMPERATURES:
    print(f"\n=== temperature {temperature}")
    answers = []
    for i in range(1, RUNS + 1):
        try:
            answers.append(ask(temperature))
        except anthropic.APIConnectionError:
            sys.exit(f"Could not reach the server at {BASE_URL} — is it running?")
        print(f"{i:>2}. {answers[-1]}")
    results[str(temperature)] = {
        "answers": answers,
        "distinct": len(set(answers)),
        "mean_similarity": round(similarity(answers), 3),
    }

RESULTS.write_text(json.dumps({"model": MODEL, "prompt": PROMPT, "runs": RUNS, "results": results}, indent=2))

print(f"\n{'temperature':<13}{'runs':>5}{'distinct answers':>18}{'mean similarity':>17}")
for temperature, r in results.items():
    print(f"{temperature:<13}{RUNS:>5}{r['distinct']:>18}{r['mean_similarity']:>17}")
print(f"\nSaved to {RESULTS.name}")
