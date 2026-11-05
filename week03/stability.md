# Week 3 — Stability test and JSON extraction

## What's here

| File | What it does |
|---|---|
| `extract_json.py` | Extracts a fixed JSON schema (model name, purpose, model type, key risks, monitoring) from short model descriptions and validates it with pydantic. If validation fails, it sends the error back to the model for one retry. |
| `stability.py` | Sends one prompt 10 times at temperature 1.0 and 10 times at 0, then measures how much the answers vary. |
| `stability_results.json` | The raw answers and metrics from the run below. |

The Anthropic prompt engineering tutorial (step 1) was worked through in a local clone that is not part of this repo.

## JSON extraction

Three fictional descriptions (a credit scorecard, a fraud model, a RAG chatbot) were all extracted and validated on the first attempt. The reliable parts of the prompt were listing the exact keys, saying "return only the JSON object", and parsing defensively, since models sometimes add fences or commentary. The validation step matters more than the prompt: a reply that parses can still have a missing key or an empty risk list, and the schema catches that. The retry path never ran in this test, so it is untested.

## Stability test

Model `gemma-4-e4b-it` on a local server, run 2026-11-05. Prompt: *"In one sentence, what is the single biggest risk of using a large language model to summarize loan documents?"*

| Temperature | Runs | Distinct answers | Mean pairwise similarity |
|---|---|---|---|
| 1.0 (server default) | 10 | 10 | 0.28 |
| 0.0 | 10 | 1 | 1.00 |

- **At 1.0, no two answers were identical.** The wording changed every time: "largest risk", "greatest risk", "biggest risk", with different consequences listed. The substance was much steadier, because 9 of the 10 answers named hallucination as the biggest risk. The tenth said the model might "subtly introduce or amplify inaccuracies", which is close to the same point.
- **At 0, all 10 answers were identical,** word for word.

The similarity score compares characters, so it measures wording, not meaning. A score of 0.28 overstates how much the answers disagreed in substance.

## What this means for a bank

- **Temperature 0 gives repeatability, which is what a validator needs.** A result that changes between runs can't be tested or reproduced. At 0 the same input gave the same output.
- **Repeatable is not the same as correct.** If the answer at temperature 0 is wrong, it is wrong every time. Week 2 showed a wrong figure in a summary, and lowering the temperature wouldn't have fixed it.
- **Differences in wording hide differences in substance.** For anything checked automatically, compare extracted fields, not raw text. That is another reason to prefer JSON output.

## Limits of this test

- One prompt, one model, 10 runs per setting. It shows the effect but doesn't measure it precisely.
- The prompt has a dominant answer. A question with several reasonable answers would vary more at temperature 1.0.
- Identical output at 0 holds for this server and hardware. A hosted API may not give bit-identical output, and the current Claude models don't accept a temperature setting at all.
- Prefill and temperature were only available on older models during the tutorial, so the tutorial ran on Claude Haiku 4.5 rather than the newest models.
