# Test questions

Fifteen questions with known answers, to check the app (Step 4). Twelve are answered in the corpus; three (13–15) are **not**, to test the "Not found in the documents." rule. Answers were checked against the extracted text on 2026-11-15; pages are the PDF page numbers.

Question 1 is the known retrieval failure from Week 5: the answer is in the index but vector search ranks that chunk 45th, so a correct app says "Not found". Count it as a retrieval miss, not a generation error.

The last two columns are from a run on 2026-11-15 with `answer.py` (qwen3-14b on the local server, temperature 0, 5 passages of 500 tokens). Every cited passage was checked against the stored chunk text.

| # | Question | Correct answer | Source file (page) | App answer | Right? |
|---|---|---|---|---|---|
| 1 | What does SR 26-2 replace? | SR letter 11-7, Guidance on Model Risk Management (April 4, 2011), and SR letter 21-8, Interagency Statement on Model Risk Management for Bank Systems Supporting BSA/AML Compliance (April 9, 2021) | SR2602-letter.pdf (p. 1) | | Not found in the documents. | Retrieval miss (expected). The letter chunk was not in the top 5; the model correctly refused rather than guess |
| 2 | How does SR 26-2 define the term "model"? | A complex quantitative method, system, or approach that applies statistical, economic, or financial theories to process input data into quantitative estimates. It excludes simple arithmetic calculations (e.g. in spreadsheets) and deterministic rule-based processes with no such theories behind them | SR2602a1.pdf (p. 3) | | Complex quantitative method/system/approach applying statistical, economic or financial theories to turn input data into quantitative estimates; excludes simple arithmetic, rule-based processes and software without such theories [SR2602a1 #1] | Yes |
| 3 | What is "effective challenge" according to SR 26-2? | Critical analysis conducted by objective experts who evaluate model risk and effect appropriate changes throughout the model lifecycle, from development to ongoing monitoring; done by people with the expertise, sufficient independence, and the organizational standing and influence to effect change | SR2602a1.pdf (p. 5) | | Not found in the documents. | No: retrieval miss. The SR 26-2 chunk with the definition ranked 39th; adding "according to SR 26-2" to the question pulled in Fed scenario chunks. The plain "What is effective challenge?" is answered from SR 11-7 and the OCC booklet |
| 4 | When was SR 11-7 issued, and by which agencies? | April 4, 2011, by the Board of Governors of the Federal Reserve System and the Office of the Comptroller of the Currency | SR11-7-guidance.pdf (p. 1) | | April 4, 2011, by the Federal Reserve Board, the OCC **and the FDIC** [SR2602-letter #0] | Partly: date right, agencies wrong. The cited letter names the three agencies as issuers of SR 26-2, not SR 11-7 (Fed and OCC). The SR 11-7 title page was not retrieved, and the model conflated the two |
| 5 | What are the three core elements of an effective validation framework in SR 11-7? | (1) Evaluation of conceptual soundness, including developmental evidence; (2) ongoing monitoring, including process verification and benchmarking; (3) outcomes analysis, including back-testing | SR11-7-guidance.pdf (p. 11) | | The three elements, correctly listed [SR11-7 #13, SR11-7-letter #3] | Yes |
| 6 | Who is the OCC's Model Risk Management booklet prepared for? | OCC examiners, for their examination and supervision of national banks, federal savings associations, and federal branches and agencies of foreign banking organizations | OCC-model-risk-booklet-2021.pdf (p. 4) | | OCC examiners, for examination and supervision of national banks, federal savings associations and federal branches/agencies [OCC #0] | Yes |
| 7 | What is the peak unemployment rate in the 2026 severely adverse scenario, and when is it reached? | 10 percent, in the third quarter of 2027 (a 5.5 percentage point rise) | Fed-2026-final-scenarios.pdf (p. 17) | | 10 percent in 3Q 2027 [Fed #14]; a 5.5 percentage point rise [Fed #5] | Yes, but the second citation is wrong: the 5.5-point figure is in passage [1] (Fed #14), not [4] (Fed #5) |
| 8 | How much do equity prices fall in the 2026 severely adverse scenario? | About 58 percent, from the fourth quarter of 2025 through the third quarter of 2026 | Fed-2026-final-scenarios.pdf (p. 18) | | About 58%, 4Q 2025 to the trough in 3Q 2026 [Fed #5, #15; PNC #2] | Yes |
| 9 | How much does real GDP decline in the 2026 severely adverse scenario? | 4.6 percent, from the fourth quarter of 2025 to its trough in the second quarter of 2027 | Fed-2026-final-scenarios.pdf (p. 19) | | 4.6 percent, 4Q 2025 to trough in 2Q 2027 [Fed #17] | Yes (slowest answer: 58 s, 1,426 output tokens of thinking) |
| 10 | What is PNC's minimum CET1 ratio in its 2026 company-run stress test? | 9.6%, in the second quarter of 2026 (actual 10.6% at 4Q 2025; 11.3% at the end of the stress period) | pnc-2026.pdf (p. 7) | | 9.6%, in 2Q 2026; regulatory minimum 4.5% [PNC #5] | Yes |
| 11 | What is Wells Fargo's minimum CET1 ratio under the 2026 severely adverse scenario? | 9.5% (actual 10.6% at Dec. 31, 2025; 11.2% at Mar. 31, 2028) | WFC-DFAST-2026.pdf (p. 5) | | 9.5% "as of March 31, 2028" [WFC #3] | Figure right, date wrong: 9.5% is the Minimum column; March 31, 2028 is the 11.2% ending column. The model misread the table row |
| 12 | What is JPMorgan Chase's projected minimum CET1 ratio in its 2026 DFAST disclosure? | 12.4% (actual 14.6%; projected 14.4% in 1Q28). The minimum is the lowest ratio over 1Q26–1Q28 | JPM-DFAST-2026.pdf (p. 6) | | 13.2% as of 1Q28 [JPM #5] | No: wrong entity. 13.2% is the minimum for JPMorgan Chase Bank, N.A. (passage [5]). The holding-company table with 12.4% was not among the 5 passages retrieved |
| 13 | What is Citigroup's minimum CET1 ratio in the 2026 stress test? | Not in the documents (Citigroup's disclosure is not in the corpus). Expected reply: "Not found in the documents." | — none — | | Not found in the documents. | Yes |
| 14 | Which OCC bulletin rescinded the Model Risk Management booklet? | Not in the documents. The booklet predates its own rescission (OCC Bulletin 2026-13 is mentioned only in our README, not in any indexed file). Expected reply: "Not found in the documents." | — none — | | Not found in the documents. | Yes. The model did not use outside knowledge, even though all 5 passages were from the OCC booklet |
| 15 | How many employees does PNC have? | Not in the documents (the stress test disclosure has no headcount). Expected reply: "Not found in the documents." | — none — | | Not found in the documents. | Yes |

## Score

| Outcome | Count | Questions |
|---|---|---|
| Right, correctly cited | 6 | 2, 5, 6, 8, 9, 10 |
| Right figure, wrong detail | 2 | 7 (cites the wrong passage for the 5.5-point rise), 11 (attaches the wrong date to the right ratio) |
| Partly right | 1 | 4 (date right; adds the FDIC, which the cited passage does not support for SR 11-7) |
| Wrong | 1 | 12 (right kind of table, wrong legal entity: the bank subsidiary instead of the holding company; the holding-company chunk ranked 23rd) |
| "Not found", should have answered | 2 | 1 (known), 3: retrieval misses, the answer was in the index but not in the top 5 |
| "Not found", correctly | 3 | 13, 14, 15 |

So 9 of 12 answerable questions got an answer (6 clean, 3 with a detail wrong), 1 was wrong, 2 were missed by retrieval, and the 3 refusals on out-of-corpus questions were all correct. The "Not found" rule fired 5 times and was never wrong to fire; the two misfires were retrieval's fault, not the model's.

**What the failures have in common.** Every wrong or missing answer traces to retrieval or to tables, not to the model inventing things:
- Questions 1 and 3 are retrieval misses: the right chunk exists but ranks 39th–45th. Phrasing matters a lot with this embedding model: "What is effective challenge?" ranks the SR 26-2 chunk 12th; adding "according to SR 26-2" drops it to 39th.
- Questions 11 and 12 are table reading: pypdf flattens a table into "10.6 % 11.2 % 9.5 %", and the model has to guess which number sits under which header. Question 12 also shows that a disclosure with two tables (holding company and bank) needs the right one retrieved, not just the right file.
- Question 4 is the one real reasoning error: the model attached the agencies named for SR 26-2 to SR 11-7. Its citation was honest, which is how the error was found.

Timing: 10–25 s per question, except question 9 (58 s) where the model thought for 1,400 tokens before answering.
