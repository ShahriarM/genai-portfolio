"""Week 0: first call to the Claude API."""
from dotenv import load_dotenv
import anthropic

load_dotenv()                      # reads ANTHROPIC_API_KEY from .env
client = anthropic.Anthropic()     # picks up the key automatically

response = client.messages.create(
    model="claude-haiku-5-5",      # small, fast, cheap model for testing
    max_tokens=200,
    messages=[
        {"role": "user",
         "content": "In two sentences, what is model risk management in banking?"}
    ],
)

print(response.content[0].text)
print("\nTokens used — input:", response.usage.input_tokens,
      "output:", response.usage.output_tokens)
