# Preserved student data card

The team asked to retain its existing student database. The read-only exporter copied the four student tables; integration did not generate or change student values. The committed CSVs rebuild these records in a fresh runtime. No real student information is claimed.

| Field | Actual provenance and coverage |
|---|---|
| Generator | Existing deterministic Python development fixture; not LLM-generated |
| Prompt/model/temperature | Not applicable; no model generation occurred |
| Counts | 30 students, 6 courses, 90 attendance rows, 90 result rows |
| Programmes | B.Tech CSE and B.Tech ECE |
| Batches | 2023 and 2024 |
| Result distribution | PASS 24, FAIL 24, ABSENT 21, DETAINED 21 |
| Validation | student_data/validation.json: valid, no violations under legacy pass-mark convention 40 |
| Exact attendance boundary | S1001 and S1005 have 75% in CS201, CS202 and CS203 |
| Below boundary | S1002 and S1006 are one attended class below 75% in those courses |
| Multiple backlogs | S1003, S1006, S1009 and seven others; full list in distribution.json |
| Demo CGPA boundary | S1001, S1004 and eight others have CGPA 7; optional fictional placement threshold |

The loader checks schema, references and logical constraints. distribution.json records actual coverage. No model-generation errors or corrections are reported because no LLM generated this kit.

Limits: regular artificial patterns; backlog totals are stored profile values rather than guaranteed aggregates of the three result rows per student. Course theory/laboratory classification, letter grade U, supplementary attempts, gender and discretionary medical condonation are missing. Supplementary eligibility requests missing authorised records. The legacy pass mark is not a universal NITJ grading rule. Batch-2025 notices do not automatically apply to this dataset.

The PDF requires an LLM-generated submission kit with saved prompts and real model provenance. Preserving this fixture does not satisfy that requirement. If generating a separate kit, save its actual prompt, model/version, generation report and validation without silently replacing these originals.
