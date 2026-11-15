"""Week 7 — the scoring set: the 12 answerable questions from week06/test_questions.md.

Each question has an `evidence` regex: a phrase from the passage that answers it. A retrieval
configuration "hits" the question when at least one retrieved chunk matches the regex, whatever
the chunk size. The three out-of-corpus questions from Week 6 are left out: they have no right chunk.
"""
QUESTIONS = [
    # (question, source file, evidence regex)
    ("What does SR 26-2 replace?",
     "SR2602-letter.pdf", r"supersedes and replaces"),
    ("How does SR 26-2 define the term \"model\"?",
     "SR2602a1.pdf", r"refers to a complex quantitative"),
    ("What is \"effective challenge\" according to SR 26-2?",
     "SR2602a1.pdf", r"effective challenge.{0,4} which refers to the critical analysis"),
    ("When was SR 11-7 issued, and by which agencies?",
     "SR11-7-guidance.pdf", r"Comptroller of the Currency April 4, 2011"),
    ("What are the three core elements of an effective validation framework in SR 11-7?",
     "SR11-7-guidance.pdf", r"three core elements"),
    ("Who is the OCC's Model Risk Management booklet prepared for?",
     "OCC-model-risk-booklet-2021.pdf", r"prepared for use by OCC examiners"),
    ("What is the peak unemployment rate in the 2026 severely adverse scenario, and when is it reached?",
     "Fed-2026-final-scenarios.pdf", r"peak of 10 percent in the third quarter of 2027"),
    ("How much do equity prices fall in the 2026 severely adverse scenario?",
     "Fed-2026-final-scenarios.pdf", r"Equity prices fall about 58 percent"),
    ("How much does real GDP decline in the 2026 severely adverse scenario?",
     "Fed-2026-final-scenarios.pdf", r"Real GDP declines 4\.6 percent"),
    ("What is PNC's minimum CET1 ratio in its 2026 company-run stress test?",
     "pnc-2026.pdf", r"minimum Basel III CET1 risk-based capital ratio of 9\.6%"),
    ("What is Wells Fargo's minimum CET1 ratio under the 2026 severely adverse scenario?",
     "WFC-DFAST-2026.pdf", r"Common Equity Tier 1 10\.6 % 11\.2 % 9\.5 %"),
    ("What is JPMorgan Chase's projected minimum CET1 ratio in its 2026 DFAST disclosure?",
     "JPM-DFAST-2026.pdf", r"Common equity tier 1 capital ratio \(%\) 14\.6% 14\.4% 12\.4%"),
]
