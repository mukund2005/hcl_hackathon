# Integration verification

Verified on 10 October 2026 with Python 3.12 on Windows. Mukund's PDF branch and the existing student records are preserved.

| Check | Result | Scope |
|---|---|---|
| Automated tests | 29 passed | API, privacy, precedence, tools, Streamlit flow and actual NITJ corpus integration; mock LLM and test-only hash embeddings |
| Data validation | Passed | 30 students, 6 courses, 90 attendance and 90 results; legacy pass mark 40 |
| Actual MiniLM indexing | Passed | Three official PDFs plus two fictional demo policies; 170 chunks and four numeric registry rules |
| Top-k 5 evaluation | 23/23 passed | Actual MiniLM + Chroma + in-process API; mock planning/explanation |
| Top-k 3 evaluation | 23/23 passed | Same corpus/questions and mock; retrieval candidate count changed |
| Actual Ollama inference | Pending | Ollama executable/model unavailable here |
| Docker build/run | Pending | Docker unavailable here |
| Live browser/server startup | Pending | In-process testing establishes code behavior, not deployment verification |

| Configuration | Case pass rate | Citation-location match | Tool correctness | Retrieval hit | Abstention | p50 / p95 ms |
|---|---|---|---|---|---|---|
| Top-k 5 | 100% | 100% | 100% | 100% | 100% | 11.07 / 29.61 |
| Top-k 3 | 100% | 100% | 100% | 100% | 100% | 9.44 / 27.09 |

Both passed this small set. Keep five candidates as a conservative default until broader real-model testing; the latency difference does not establish a reliable advantage. Reports are evaluation/nitj_top5_report.json and nitj_top3_report.json, with per-case CSVs. Zero LLM calls/tokens means no inference calls occurred. These are not real LLM accuracy, cost or latency measurements. Embedding startup time is outside per-question latency.

Checks compare answer types, selected answer substrings, source/section/page, selected exact numeric fields and audit retrieval hits. Citation-location matching does not establish semantic support; a human must grade cited clauses. The latency percentile uses the script's ordered-sample estimator across 23 requests. Three exported audit examples disclose the same development mode.

Remaining work: actual Ollama, Docker smoke test, confirmed effectivity dates, human citation grading, real LLM-generated data provenance and personal team declarations. See REQUIREMENTS_STATUS.md.
