"""Week 3 — Prompting properly: extract a fixed JSON schema from model descriptions and validate it in Python."""
import json
import re
import sys

import anthropic
from pydantic import BaseModel, Field, ValidationError

BASE_URL = "http://localhost:8079"   # on the T480s: "http://localhost:8081"
MODEL = "gemma-4-e4b-it"             # must be the model loaded on the server
MAX_TOKENS = 3000                    # leaves room for the model's thinking plus the JSON
TIMEOUT = 300
MAX_ATTEMPTS = 2                     # one retry, with the validation error fed back to the model

# Short fictional model descriptions, written for this exercise
SAMPLES = {
    "scorecard": """The Retail Application Scorecard (RAS v3.2) is a logistic regression model used by the consumer
lending division to decide whether to approve new personal-loan applications. It was developed on 2019-2023 application
data and is recalibrated annually. Known weaknesses: it performs poorly for applicants with thin credit files, and its
coefficients have not been tested under a recession scenario. Performance is monitored monthly through the Gini
coefficient and the population stability index; a PSI above 0.25 triggers a review.""",
    "fraud": """FraudNet is a gradient-boosted tree model that scores card transactions in real time and blocks those
above a risk threshold. It was trained on 18 months of labelled chargeback data. The main risks are concept drift as
fraudsters change tactics, a high false-positive rate on cross-border purchases, and dependence on a third-party device
fingerprint feed. The model is retrained quarterly and its alert rate is reviewed weekly.""",
    "chatbot": """The Policy Assistant is a retrieval-augmented chatbot that answers staff questions about internal
compliance policies. It uses a hosted large language model and a vector index of 400 policy documents. Risks include
hallucinated answers, out-of-date documents in the index, and exposure of confidential text in prompts sent to the
vendor. Answers must cite a policy section, and a sample of 50 conversations is reviewed by compliance each month.""",
}


class ModelCard(BaseModel):
    """The fixed schema every extraction must satisfy."""
    model_name: str
    purpose: str
    model_type: str
    key_risks: list[str] = Field(min_length=1)
    monitoring: str


SYSTEM_PROMPT = "You extract structured data from bank model documentation. Use only facts stated in the text."
INSTRUCTIONS = """Read the model description and return a JSON object with exactly these keys:
- "model_name": string
- "purpose": string, one sentence
- "model_type": string, for example "logistic regression"
- "key_risks": array of short strings, one per risk named in the text
- "monitoring": string, one sentence

Return only the JSON object, with no commentary and no code fences."""

client = anthropic.Anthropic(base_url=BASE_URL, api_key="none", timeout=TIMEOUT)


def ask(messages):
    msg = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, system=SYSTEM_PROMPT, messages=messages)
    # the reply can start with a thinking block, so keep only the text blocks
    return "".join(b.text for b in msg.content if b.type == "text")


def parse(reply):
    """Pull the JSON object out of the reply (models sometimes add fences or chatter) and validate it."""
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if not match:
        raise ValueError("no JSON object found in the reply")
    return ModelCard.model_validate(json.loads(match.group(0)))


def extract(description):
    messages = [{"role": "user", "content": f"{INSTRUCTIONS}\n\n<description>\n{description}\n</description>"}]
    for attempt in range(1, MAX_ATTEMPTS + 1):
        reply = ask(messages)
        try:
            return parse(reply), attempt
        except (ValueError, ValidationError) as e:   # JSONDecodeError is a ValueError
            print(f"  attempt {attempt} failed validation: {str(e).splitlines()[0]}")
            messages += [{"role": "assistant", "content": reply},
                         {"role": "user", "content": f"That was not valid. Error: {e}\nReturn only the corrected JSON object."}]
    return None, MAX_ATTEMPTS


failures = 0
for name, description in SAMPLES.items():
    print(f"\n=== {name}")
    try:
        card, attempts = extract(description)
    except anthropic.APIConnectionError:
        sys.exit(f"Could not reach the server at {BASE_URL} — is it running?")
    if card is None:
        failures += 1
        print("  FAILED: no valid JSON after", MAX_ATTEMPTS, "attempts")
        continue
    print(f"  valid after {attempts} attempt(s)")
    print(card.model_dump_json(indent=2))

print(f"\n{len(SAMPLES) - failures}/{len(SAMPLES)} descriptions extracted and validated")
