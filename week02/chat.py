"""Week 2 — Calling models from Python."""
import sys

import anthropic

BASE_URL = "http://localhost:8079"   # on the T480s: "http://localhost:8081"
MODEL = "gemma-4-e4b-it"             # must be the model loaded on the server
MAX_TOKENS = 1500                    # leaves room for the model's thinking plus the answer
TIMEOUT = 120                        # seconds to wait before giving up on the server

SYSTEM_PROMPT = "You are a concise assistant who explains ideas to bank risk analysts."
USER_MESSAGE = "Explain recursion briefly."

client = anthropic.Anthropic(
    base_url=BASE_URL,
    api_key="none",                  # local server ignores the key
    timeout=TIMEOUT,
    max_retries=2,                   # the SDK retries rate-limit and timeout errors before raising
)

try:
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_MESSAGE}],
    ) as stream:
        # text_stream yields only answer text, so the thinking block is skipped
        for text in stream.text_stream:
            print(text, end="", flush=True)
        msg = stream.get_final_message()
except anthropic.RateLimitError:
    sys.exit("\nRate limit hit — wait a moment and try again.")
except anthropic.APITimeoutError:
    sys.exit(f"\nNo reply within {TIMEOUT} seconds — the model may be busy or thinking too long.")
except anthropic.APIConnectionError:
    sys.exit(f"\nCould not reach the server at {BASE_URL} — is it running?")

print("\n\nTokens used — input:", msg.usage.input_tokens,
      "output:", msg.usage.output_tokens)
