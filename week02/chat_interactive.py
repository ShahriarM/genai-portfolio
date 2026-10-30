"""Week 2 — Calling models from Python: interactive chat in the terminal."""
import sys

import anthropic

BASE_URL = "http://localhost:8079"   # on the T480s: "http://localhost:8081"
MODEL = "gemma-4-e4b-it"             # must be the model loaded on the server
MAX_TOKENS = 1500                    # leaves room for the model's thinking plus the answer
TIMEOUT = 120                        # seconds to wait before giving up on the server

SYSTEM_PROMPT = "You are a concise assistant who explains ideas to bank risk analysts."

client = anthropic.Anthropic(
    base_url=BASE_URL,
    api_key="none",                  # local server ignores the key
    timeout=TIMEOUT,
    max_retries=2,                   # the SDK retries rate-limit and timeout errors before raising
)

messages = []                        # the whole conversation, resent each turn so the model remembers it

print(f"Chatting with {MODEL}. Type 'quit' or press Ctrl+D to exit.\n")

while True:
    try:
        user_message = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break
    if user_message.lower() in ("quit", "exit"):
        break
    if not user_message:
        continue

    messages.append({"role": "user", "content": user_message})
    print("Model: ", end="", flush=True)

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            # text_stream yields only answer text, so the thinking block is skipped
            reply = ""
            for text in stream.text_stream:
                print(text, end="", flush=True)
                reply += text
            msg = stream.get_final_message()
    except anthropic.RateLimitError:
        print("\nRate limit hit — wait a moment and try again.\n")
        messages.pop()               # drop the unanswered message so you can resend it
        continue
    except anthropic.APITimeoutError:
        print(f"\nNo reply within {TIMEOUT} seconds — the model may be busy or thinking too long.\n")
        messages.pop()
        continue
    except anthropic.APIConnectionError:
        sys.exit(f"\nCould not reach the server at {BASE_URL} — is it running?")
    except KeyboardInterrupt:
        print("\n[reply interrupted]\n")
        messages.pop()
        continue

    messages.append({"role": "assistant", "content": reply})
    print(f"\n[tokens — input: {msg.usage.input_tokens}, output: {msg.usage.output_tokens}]\n")
