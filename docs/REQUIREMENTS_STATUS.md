# PDF contract and remaining submission work

| Requirement | Integration status |
|---|---|
| R1 retrieval | Actual MiniLM, persisted Chroma, three official NITJ PDFs from Mukund's branch |
| R2 citations | Document, section/page, version and effective date; exact commencement day of UG 2023 still needs confirmation |
| R3 abstention | Exact not_found message; partial eligibility explicitly disclosed |
| R4 versions | Scope, explicit supersession, authority, recency and unresolved conflicts for numeric registry rules; arbitrary procedural conflicts remain conservative |
| R5 tools | SQLite and Python attendance, results and placement conditions; no LLM arithmetic |
| R6 multi-step | Hypothetical backlog clearance and profile check; unchanged CGPA assumption. Supplementary certification requires missing grade/attempt/type records |
| R7 identity | Header-only student context and cross-student refusal; production authentication is outside this prototype |
| R8 untrusted text | Constrained plans, parameterised SQL, instruction-pattern filtering. Not a guarantee against all prompt injection |
| R9 response typing | All six specified types; JSON API and JSON/text UI |
| R10 audit | Trace, retrieved/applied sources, tools, rules, conflicts, model, usage and latency; sample audits stored in evaluation/audits |
| R11 live ingestion | Authenticated admin endpoint publishes immediately; unsupported numeric amendments reject without changing stores |
| R12 evaluation | 23-case measured development reports and top-k comparison; real Ollama and human semantic citation grading pending |
| Required stack | Streamlit, FastAPI/Uvicorn/Pydantic2, LangGraph, Chroma, SQLite, MiniLM, Ollama adapter, Docker compose, Git |
| Data minimum | Existing synthetic 30 students, 2 programmes, 2 batches, 6 courses; counts and logical validation pass |
| LLM-generated data kit | **Not complete:** retained records were deterministic Python fixtures, per user instruction to preserve them. Generator exists; do not invent model/prompt provenance |
| Official corpus | Three reviewed official PDFs, with scoped notice windows; one documented screenshot exclusion, OCR absent |
| Synthetic document limit | Zero default; two optional demo policies. Legacy test fixtures are never loaded by final setup |
| Docker verification | Packaging and readiness ordering implemented; actual Docker run pending |
| Original-work declarations | Team must sign their own. Contribution/AI disclosure templates included |

An implementation tag records a code checkpoint, not a claim that pending requirements were achieved.
