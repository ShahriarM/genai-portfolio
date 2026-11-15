# Week 8 — Tool use

Deliverable: the three tools and a log of a multi-step question.

## Layout

| Path | Purpose |
|---|---|
| `make_data.py` | Builds `loans.db`: 500 **synthetic** loans (amount, FICO, DTI, LTV, term, state, defaulted), fixed seed. Done |
| `loans.db` | The SQLite table the SQL tool queries. Rebuild with `python make_data.py` |
| `tools.py` | The three tools and their schemas: `calculator` (arithmetic parsed with `ast`, no `eval`), `sql_query` (read-only, one SELECT, at most 200 rows), `get_pd` (logistic regression on FICO, DTI, LTV; by `loan_ids` or for one hypothetical loan) |
| `agent.py` | The tool-use loop and the audit log. `python agent.py "question"` prints the tool calls and the answer |
| `test_agent.py` | Tests of the loop's controls with a faked model, no server needed: `python test_agent.py` |
| `logs/` | One JSON-lines file per question: the question, each model turn (with its thinking), every tool call with input, output, error flag and duration, and the answer |
| `logs/first_run_parallel_calls/` | The two logs from the first run, kept as evidence of the failure described below |

## The data

`loans.db` has one table, `loans`, with 500 made-up loans: 24 defaults (4.8%), 157 loans over $300k, average amount about $264,000. Default was simulated from a logistic function of FICO, DTI and LTV, so a logistic model fitted on the table recovers a real relationship. It describes no actual borrowers.

## Steps (from the study plan)

1. Read the tool-use documentation: you describe a function with a JSON schema, the model asks to call it, your code runs it and returns the result.
2. Build three tools: a calculator, a SQL query over a small SQLite table of loan data, and a function that returns a PD from a simple logistic model you fit.
3. Ask questions that require combining tools, such as "What is the average PD for loans over $300k?"
4. Log every tool call and result so you can audit what the model did.

## Notes

- The model runs on the local llama.cpp server (`qwen3-14b`). Its Anthropic-compatible endpoint supports tool calls: a calculator round trip was verified on 2026-11-15 (`stop_reason: "tool_use"`, then `end_turn` after the `tool_result`).
- The tools take model-written input, so each one is a control point: the calculator must not `eval`, and the SQL tool must be read-only and row-capped. That is the model-risk angle of this week.

## The multi-step question

Run on 2026-11-15 with qwen3-14b, log `logs/20261115-125213.jsonl`:

> For loans over $300k: what is the average PD, and what is the expected loss if expected loss = average PD x total balance x 45% loss given default?

| Round | Tool call | Result |
|---|---|---|
| 1 | `sql_query`: loan_id and amount of loans over $300k | 157 rows |
| 2 | `get_pd` with those 157 loan_ids | mean PD 0.043687 |
| 3 | `sql_query`: `SUM(amount)` for the same loans | 70,461,000 |
| 4 | `calculator`: `0.043687 * 70461000 * 0.45` | 1,385,203.37 |

Answer: average PD 4.37%, expected loss $1,385,203. Checked independently against the table and the model: 157 loans, mean PD 0.043687, balance $70,461,000. (With the unrounded mean the product is $1,385,194; the $9 difference is the PD tool rounding to six decimals.)

## What broke

**The first run gave a confident wrong answer, and only the log showed it.** In one turn the model asked for four tools at once: the two SQL queries, then `get_pd` and `calculator` with inputs it could not know yet. It invented them: loan ids `12345, 67890, 11223, ...` and the expression `0.0312 * 15000000 * 0.45`. `get_pd` returned an error (no such ids), the calculator happily returned 210,600, and the final answer reported an average PD of 3.12% and an expected loss of $210,600, stating that `get_pd` "with corrected loan_ids" had returned 3.12%. It never had. The true figures are 4.37% and $1.39 million.

Two details matter:
- The 0.0312 came from the example in my own calculator description. A number in a tool description can end up in an answer. The description now has no figures.
- The answer's own account of its steps was false. It quoted the right total balance, a PD no tool produced, and an expression different from the one it ran. Only the logged tool inputs and outputs show what happened.

**Controls added.** The system prompt now says to call one tool at a time and never use a value that a tool result did not supply. The loop also enforces it: only the first tool call of a turn is run, and any others get an error result telling the model to call again with real figures. After the prompt change both test questions ran one call per round and were correct, so the enforcement in the loop has not fired in a live run. `test_agent.py` covers it instead, with a faked model that replays the failure: it asks for a SQL query and a calculator call with invented numbers in one turn. The test checks that only the SQL query runs, that the calculator call gets the error result and is still logged, and that the invented result never reaches the model. A second test checks the round limit. Both pass, and the first fails when the control is removed.

## Limits

- Two questions, one model, one run each at temperature 0. That shows the loop works and shows one failure mode; it does not measure how often the model gets it right.
- Nothing checks the final answer against the tool results. A model can still misquote a figure it was given. The log makes that auditable, not impossible.
- The PD model is fitted and applied on the same 500 synthetic loans, with no holdout. It is a prop for the tool, not a validated model.
- `sql_query` blocks writes and caps rows, but any SELECT is allowed, including slow ones. Fine for a 500-row table.

