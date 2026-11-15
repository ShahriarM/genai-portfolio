"""Week 8 — Tool use: the loop that lets the model call the tools, with an audit log.

    python agent.py "What is the average PD for loans over $300k?"

The model never runs a tool. It returns a tool_use block (a name and JSON arguments); this script
runs the matching function, sends the result back as a tool_result, and asks again, until the model
answers in text. Every step is appended to a JSON-lines file in logs/, so the run can be audited.
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import anthropic

from tools import FUNCTIONS, TOOLS

BASE_URL = "http://localhost:8079"   # local llama.cpp server; tool calls verified with qwen3-14b on 2026-11-15
MODEL = "qwen3-14b"
MAX_TOKENS = 4000                    # thinking plus a tool call that may list many loan ids
MAX_ROUNDS = 10                      # model calls per question, so a confused model cannot loop forever
LOGS = Path(__file__).resolve().parent / "logs"

SYSTEM_PROMPT = """You answer questions about a bank's loan portfolio for risk analysts.

- Get every figure from a tool. Never state a number from memory or estimate one.
- Do every calculation with the calculator, including simple ones.
- Plan the steps first: which tool gives which number, and how they combine.
- Call ONE tool at a time and wait for its result. Never put a number or an id into a tool call
  unless a tool result in this conversation gave it to you. Do not use placeholder values.
- If a tool returns an error, read it, fix the call and try again.
- In the final answer, give the result and list the steps and figures it came from."""

# The model sometimes asks for several tools at once and invents the inputs of the later ones, because
# it has not seen the earlier results yet. Only the first call of a round is run; the rest get this.
ONE_AT_A_TIME = ("Not run: only one tool call is run per turn, so that each call can use the previous result. "
                 "Call this tool again now, using figures from the results you have received.")

client = anthropic.Anthropic(base_url=BASE_URL, api_key="none", timeout=300)


def run_tool(name, tool_input):
    """Run one tool call. Returns (result text, is_error); errors go back to the model, not up the stack."""
    if name not in FUNCTIONS:
        return f"Unknown tool: {name}. Available: {', '.join(FUNCTIONS)}", True
    try:
        return FUNCTIONS[name](**tool_input), False
    except (ValueError, TypeError) as e:        # bad input from the model: say why, so it can correct itself
        return f"Error: {e}", True


def ask(question, log_path=None):
    """Run the tool loop for one question. Returns the final answer; writes the audit log."""
    LOGS.mkdir(exist_ok=True)
    log_path = log_path or LOGS / f"{datetime.now():%Y%m%d-%H%M%S}.jsonl"

    def log(event, **fields):
        with open(log_path, "a") as f:
            f.write(json.dumps({"time": datetime.now().isoformat(timespec="seconds"), "event": event, **fields}) + "\n")

    log("question", question=question, model=MODEL, tools=[t["name"] for t in TOOLS])
    messages = [{"role": "user", "content": question}]

    for round_no in range(1, MAX_ROUNDS + 1):
        response = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS, system=SYSTEM_PROMPT, tools=TOOLS, messages=messages,
            extra_body={"temperature": 0},
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        log("model", round=round_no, stop_reason=response.stop_reason, text=text,
            thinking="".join(b.thinking for b in response.content if b.type == "thinking").strip(),
            input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens)

        if response.stop_reason != "tool_use":                 # end_turn, or max_tokens: either way the loop is over
            if response.stop_reason == "max_tokens":
                text += "\n[The reply was cut off at the token limit.]"
            log("answer", answer=text, rounds=round_no)
            return text, log_path

        messages.append({"role": "assistant", "content": response.content})   # unchanged, tool_use blocks included
        results = []
        for n, block in enumerate(b for b in response.content if b.type == "tool_use"):
            start = time.monotonic()
            if n == 0:
                output, is_error = run_tool(block.name, block.input)
            else:                                              # control: one call per round (see README, "What broke")
                output, is_error = ONE_AT_A_TIME, True
            log("tool_call", round=round_no, tool=block.name, input=block.input, output=output,
                is_error=is_error, seconds=round(time.monotonic() - start, 3))
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output, "is_error": is_error})
        messages.append({"role": "user", "content": results})  # all results of this round in ONE user message

    log("answer", answer=None, rounds=MAX_ROUNDS, stopped="round limit reached")
    return f"Stopped after {MAX_ROUNDS} rounds without a final answer.", log_path


def print_log(log_path):
    """A readable trace of the run, from the log file itself."""
    for line in open(log_path):
        e = json.loads(line)
        if e["event"] == "tool_call":
            flag = " ERROR" if e["is_error"] else ""
            shown = json.dumps(e["input"])
            print(f"  [{e['round']}] {e['tool']}({shown[:150]}{'...' if len(shown) > 150 else ''}){flag}\n      -> {e['output'][:200]}{'...' if len(e['output']) > 200 else ''}")


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What is the average PD for loans over $300k?"
    start = time.monotonic()
    try:
        answer, log_path = ask(question)
    except anthropic.APIConnectionError:
        sys.exit(f"Could not reach the server at {BASE_URL} — is it running?")
    except anthropic.APITimeoutError:
        sys.exit("The server did not reply in time.")
    print(f"Q: {question}\n\nTool calls:")
    print_log(log_path)
    print(f"\nA: {answer}\n\nLog: {log_path.relative_to(Path.cwd()) if log_path.is_relative_to(Path.cwd()) else log_path}  ({time.monotonic() - start:.0f} s)")
