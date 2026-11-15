"""Week 8 — test of the loop's one-call-per-turn control, with a faked model (no server needed).

The fake model asks for two tools in its first turn: a real SQL query, and a calculator call with
numbers it could not know yet. The loop must run only the first and refuse the second.

    python test_agent.py
"""
import copy
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS

import agent


def tool_use(id_, name, input_):
    return NS(type="tool_use", id=id_, name=name, input=input_)


def reply(stop_reason, *content):
    return NS(stop_reason=stop_reason, content=list(content), usage=NS(input_tokens=0, output_tokens=0))


class FakeMessages:
    """Stands in for client.messages: returns scripted replies and records what it was sent."""

    def __init__(self, replies):
        self.replies, self.sent = list(replies), []

    def create(self, **kwargs):
        self.sent.append(copy.deepcopy(kwargs["messages"]))      # a copy: the loop keeps appending to the list
        return self.replies.pop(0)


def test_only_first_tool_call_of_a_turn_runs():
    fake = FakeMessages([
        reply("tool_use",
              tool_use("a", "sql_query", {"query": "SELECT SUM(amount) FROM loans WHERE amount > 300000"}),
              tool_use("b", "calculator", {"expression": "0.0312 * 15000000 * 0.45"})),   # invented inputs
        reply("end_turn", NS(type="text", text="done")),
    ])
    calls = []
    real = dict(agent.FUNCTIONS)
    agent.client = NS(messages=fake)
    agent.FUNCTIONS = {name: (lambda n: lambda **kw: calls.append(n) or real[n](**kw))(name) for name in real}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "test.jsonl"
            answer, _ = agent.ask("test question", log_path=log_path)
            events = [json.loads(line) for line in open(log_path)]
    finally:
        agent.FUNCTIONS = real

    assert calls == ["sql_query"], f"only the first tool may run, but these ran: {calls}"

    results = fake.sent[1][-1]                                   # last message of the second request
    assert results["role"] == "user" and len(results["content"]) == 2, "both results go back in one user message"
    first, second = results["content"]
    assert (first["tool_use_id"], first["is_error"]) == ("a", False) and "70461000" in first["content"]
    assert (second["tool_use_id"], second["is_error"]) == ("b", True) and second["content"] == agent.ONE_AT_A_TIME
    assert "210600" not in str(fake.sent), "the invented calculation must never reach the model as a result"

    logged = [e for e in events if e["event"] == "tool_call"]
    assert [(e["tool"], e["is_error"]) for e in logged] == [("sql_query", False), ("calculator", True)]
    assert logged[1]["input"] == {"expression": "0.0312 * 15000000 * 0.45"}, "the refused call's input is still logged"
    assert answer == "done"


def test_round_limit_stops_a_looping_model():
    endless = [reply("tool_use", tool_use(str(i), "calculator", {"expression": "1 + 1"})) for i in range(agent.MAX_ROUNDS + 5)]
    fake = FakeMessages(endless)
    agent.client = NS(messages=fake)
    with tempfile.TemporaryDirectory() as tmp:
        answer, _ = agent.ask("loop forever", log_path=Path(tmp) / "test.jsonl")
    assert len(fake.sent) == agent.MAX_ROUNDS and "Stopped after" in answer


if __name__ == "__main__":
    for test in (test_only_first_tool_call_of_a_turn_runs, test_round_limit_stops_a_looping_model):
        test()
        print("passed:", test.__name__)
