"""Export three actual API audits from the configured runtime."""
import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app


def main():
    examples = [
        ("calculated", "Am I eligible for the CS201 exam?"),
        ("retrieved", "What is the attendance requirement?"),
        ("not_found", "What is the cafeteria menu today?"),
    ]
    output = Path("evaluation/audits")
    output.mkdir(parents=True, exist_ok=True)
    with TestClient(create_app()) as client:
        for name, question in examples:
            headers = {"X-Student-Id": "S1001"}
            response = client.post("/ask", headers=headers, json={
                "question": question, "as_of_date": "2026-07-01",
            })
            response.raise_for_status()
            answer = response.json()
            audit = client.get("/audit/" + answer["trace_id"], headers=headers)
            audit.raise_for_status()
            record = {"health": client.get("/health").json(), "response": answer, "audit": audit.json()}
            (output / (name + ".json")).write_text(json.dumps(record, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
