"""Small disclosed exact/type/source benchmark. Run against an actual API."""
import argparse
import csv
import json
import statistics
import time
from contextlib import nullcontext
from pathlib import Path
import httpx


def run(api, output, questions, client=None):
    records, times = [], []
    with (nullcontext(client) if client is not None else httpx.Client(timeout=180)) as client:
        health = client.get(api + "/health").json()
        for case in json.loads(Path(questions).read_text(encoding="utf-8")):
            started = time.perf_counter()
            response = client.post(api + "/ask", headers={"X-Student-Id": case["student"]} if case.get("student") else {},
                                   json={"question": case["question"], "as_of_date": case.get("date", "2026-10-10")})
            response.raise_for_status()
            actual = response.json()
            ms = (time.perf_counter() - started) * 1000
            times.append(ms)
            type_ok = actual["answer_type"] == case["type"]
            content_ok = case.get("contains", "") in actual["answer"]
            source_ok = not case.get("source") or any(c["doc_id"] == case["source"] for c in actual["citations"])
            citation_ok = source_ok and all(any(c.get(key) == value for c in actual["citations"] if c["doc_id"] == case["source"])
                                            for key,value in case.get("expected_citation",{}).items())
            tool_ok = True
            if case.get("expected_result"):
                payload = json.loads(actual["answer"]) if actual["answer_type"] == "calculated" else {}
                tool_ok = all(payload.get(key) == value for key,value in case["expected_result"].items())
            audit = client.get(api + "/audit/" + actual["trace_id"],
                               headers={"X-Student-Id":case["student"]} if case.get("student") else {}).json()
            retrieval_ok = any(c["doc_id"] == case.get("source") for c in audit.get("sources_retrieved", []))
            records.append({"id": case["id"], "expected_type": case["type"], "actual_type": actual["answer_type"],
                            "passed": type_ok and content_ok and citation_ok and tool_ok, "source_expected": bool(case.get("source")),
                            "source_ok": source_ok, "citation_ok":citation_ok, "tool_checked":bool(case.get("expected_result")), "tool_ok":tool_ok,
                            "retrieval_checked":bool(case.get("retrieval_checked")), "retrieval_ok":retrieval_ok,
                            "abstention_ok":(actual["answer_type"] == "not_found") == (case["type"] == "not_found"),
                            "llm_calls":audit.get("llm_calls",0), "tokens":audit.get("tokens",0),
                            "latency_ms": round(ms, 2), "trace_id": actual["trace_id"]})
    source_cases = [r for r in records if r["source_expected"]]
    tool_cases = [r for r in records if r["tool_checked"]]
    retrieval_cases = [r for r in records if r["retrieval_checked"]]
    summary = {"mode": "development-mock" if health["mock_llm"] else "ollama", "embedding_backend": health["embedding_backend"],
               "cases": len(records), "passed": sum(r["passed"] for r in records),
               "case_pass_rate": sum(r["passed"] for r in records) / len(records),
               "expected_source_presence": sum(r["source_ok"] for r in source_cases) / len(source_cases) if source_cases else None,
               "citation_location_accuracy":sum(r["citation_ok"] for r in source_cases) / len(source_cases) if source_cases else None,
               "tool_result_correctness":sum(r["tool_ok"] for r in tool_cases) / len(tool_cases) if tool_cases else None,
               "retrieval_hit_rate":sum(r["retrieval_ok"] for r in retrieval_cases) / len(retrieval_cases) if retrieval_cases else None,
               "abstention_accuracy":sum(r["abstention_ok"] for r in records) / len(records),
               "mean_llm_calls":statistics.mean(r["llm_calls"] for r in records),
               "total_tokens":sum(r["tokens"] for r in records),
               "latency_p50_ms": round(statistics.median(times), 2),
               "latency_p95_ms": round(sorted(times)[max(0, int(len(times) * .95) - 1)], 2),
               "method": "Exact answer types and supplied numeric tool fields, answer substrings, expected citation locations, audit retrieval hit and abstention. Citation location accuracy does not establish semantic support; manually review the cited clauses. Mock tokens are zero, not a real inference cost measurement.",
               "results": records}
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with output.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--output", default="runtime/evaluation.json")
    parser.add_argument("--questions", default="evaluation/questions.json")
    parser.add_argument("--in-process", action="store_true", help="Use the ASGI API directly when loopback networking is unavailable")
    args = parser.parse_args()
    if args.in_process:
        from fastapi.testclient import TestClient
        from app.main import create_app
        with TestClient(create_app()) as client:
            run("http://testserver", args.output, args.questions, client)
    else:
        run(args.api, args.output, args.questions)
