# Source documents

New documents for Week 5, downloaded on 2026-11-08 from the publishers' own sites. Three more documents already in the repo are used as well (listed in `../README.md`). All are public.

| File | What it is | Pages | Source |
|---|---|---|---|
| `SR11-7-guidance.pdf` | *Supervisory Guidance on Model Risk Management*, April 2011. The Federal Reserve and OCC guidance that SR 26-2 replaced | 21 | federalreserve.gov (`boarddocs/srletters/2011/sr1107a1.pdf`) |
| `SR11-7-letter.pdf` | The SR 11-7 cover letter | 5 | federalreserve.gov (`boarddocs/srletters/2011/sr1107.pdf`) |
| `SR2602-letter.pdf` | The SR 26-2 cover letter (April 17, 2026), which names the letters SR 26-2 supersedes: SR 11-7 and SR 21-8. Pages 1–2 of `../../week04/docs/SR2602.pdf`, extracted with pypdf on 2026-11-14 so the guidance text is not indexed twice | 2 | federalreserve.gov, via `week04/docs/SR2602.pdf` |
| `Fed-2026-final-scenarios.pdf` | Federal Reserve final 2026 supervisory stress test scenarios (hypothetical recession, February 2026) | 42 | federalreserve.gov (`publications/files/2026-final-supervisory-stress-test-scenarios-20260204.pdf`) |
| `Fed-2026-macro-model-guide.pdf` | Federal Reserve supervisory stress test documentation: final 2026 macroeconomic model guide | 69 | federalreserve.gov (`supervisionreg/files/2026-final-macroeconomic-model-guide.pdf`) |
| `Fed-2026-global-market-shock.pdf` | Federal Reserve supervisory stress test documentation: final 2026 global market shock component | 85 | federalreserve.gov (`supervisionreg/files/2026-final-gms-model.pdf`) |
| `BAC-DFAST-2026.pdf` | Bank of America 2026 Dodd-Frank Act annual stress test results | 22 | Bank of America investor relations |
| `JPM-DFAST-2026.pdf` | JPMorgan Chase 2026 annual Dodd-Frank Act stress test results disclosure, June 24, 2026 | 20 | jpmorganchase.com |
| `MS-DFAST-2026.pdf` | Morgan Stanley 2026 Dodd-Frank Act stress test disclosure | 15 | morganstanley.com |
| `WFC-DFAST-2026.pdf` | Wells Fargo 2026 annual stress test results, July 2026 | 13 | wellsfargo.com |

## Notes

- The Fed documents are the supervisor's own scenarios and model descriptions. The bank files are the company-run disclosures. They cover similar topics in different words, which suits retrieval tests.
- SR 11-7 is superseded by SR 26-2, and the SR 26-2 cover letter says so, so the corpus contains the answer to "What does SR 26-2 replace?". Whether search *finds* it is another matter: see `../../week06/README.md`.
- The bank links are from the banks' investor-relations sites and may move. The files here are the copies used.
- Text was checked with `pdftotext` and is selectable in every file, so no OCR is needed.
- Total in the corpus with the three existing documents: 13 documents, about 175,000 words.
