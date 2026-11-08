# Generative AI Portfolio

A 16-week, hands-on build of generative AI skills, applied to financial risk and model governance.

## Goal

Reach builder-level skill in generative AI — retrieval-augmented generation (RAG), agents and tool use, evaluation, guardrails and cloud deployment — and document each step with working code.

## Approach

I treat every LLM system the way a bank treats a credit model: defined purpose, controlled data, rigorous testing, documented limitations and ongoing monitoring. The capstone is a RAG application on public model risk guidance (e.g. SR 26-2), delivered with an evaluation framework and a validation report in the style of a bank model risk review.

## Structure

| Folder | Topic |
|---|---|
| `week01`–`week04` | LLM foundations, API use, prompting, embeddings |
| `week05`–`week10` | RAG, retrieval tuning, tool use, agents, frameworks |
| `week11`–`week14` | Evaluation, guardrails, AI model risk, capstone |
| `week15`–`week16` | Containerization and cloud deployment |

## Setup

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Create a `.env` file with `ANTHROPIC_API_KEY=...` (never committed).

## Status

- [x] Week 0 — environment setup
- [x] Week 1 — how LLMs work
- [x] Week 2 — calling models from Python
- [x] Week 3 — prompting properly
- [x] Week 4 — embeddings and similarity