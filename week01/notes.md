# Week 1 — How LLMs work

## Key terms

- **Token:** the unit a model reads and writes, a word or part of a word (about ¾ of an English word on average). Every limit and every bill is counted in tokens.
- **Pre-training:** training on a huge amount of text with one objective: predict the next token. This is where the model picks up language, facts and patterns. It is expensive and done once per model.
- **Fine-tuning:** further training of a pre-trained model on narrower data, such as example conversations and human preference ratings, so it follows instructions and behaves like an assistant rather than just continuing text.
- **Context window:** the maximum number of tokens the model can take into account at once: system prompt, conversation history, documents and its own reply. My local server runs Gemma with a 16,384-token window. Anything outside it simply doesn't exist for the model.

## What an LLM computes

Given a sequence of tokens, an LLM outputs a **probability distribution over the next token**. That's all it does. A reply is produced one token at a time: pick a token from the distribution, append it to the input, and run the model again.

The core of the computation is **attention**. Each token's vector is multiplied by three learned matrices to give a query (Q), a key (K) and a value (V):

    Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V

- Q·Kᵀ scores how relevant every earlier token is to the current one (a dot product, so a similarity).
- Dividing by √d_k keeps the scores from growing with vector size, so the softmax doesn't saturate.
- The softmax turns the scores into weights that sum to 1.
- The output is a weighted average of the value vectors: each token gathers information from the tokens that matter to it.

A transformer stacks many attention layers, each with several heads, plus feed-forward layers. The final vector is mapped to a score (logit) for every token in the vocabulary.

## Why it hallucinates

The model is trained to produce **plausible** text, not **true** text. It has no separate store of facts and no built-in check against a source. When the right answer is missing, rare in training, or buried in a long context, the most probable next tokens can still form a fluent, confident and wrong statement. Sampling adds randomness on top, so one unlucky token early on can send the rest of the answer the wrong way.

I saw this in Week 2: summarizing PNC's stress test disclosure, Gemma 4B labelled the commercial real estate loss ($2.9B) as residential real estate, which is actually $1.4B in the source. It read just as confidently as the correct figures. Giving the model the source text (as RAG does later in this plan) reduces hallucination but doesn't remove it, so outputs still have to be checked.

## What temperature does

Temperature T rescales the logits before the softmax:

    p_i = exp(z_i / T) / Σ_j exp(z_j / T)

- **T < 1** sharpens the distribution: the likeliest tokens dominate and answers become focused and repeatable. As T → 0 it always picks the top token (greedy decoding).
- **T = 1** uses the model's distribution unchanged.
- **T > 1** flattens it: unlikely tokens get picked more often, so output is more varied, and past about 2 it becomes incoherent.

It usually works alongside **top-k** (sample only from the k likeliest tokens) and **top-p** (sample only from the smallest set whose probabilities add up to p). My local server's defaults are temperature 1.0, top-k 64, top-p 0.95 and min-p 0.05.

Low temperature does **not** make answers more correct. It makes them more consistent: a model that is wrong at T = 0 is wrong every time. For a bank, consistency is still worth having, because a result that changes from run to run can't be validated. Week 3 tests this directly.
