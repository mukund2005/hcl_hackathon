
# scripts/04_make_chunks.py

from pathlib import Path
import json
import re
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
REGISTER = BASE / "source_register.csv"
EXTRACTED = BASE / "extracted_text"
OUTPUT = EXTRACTED / "chunks.jsonl"

CHUNK_WORDS = 700
OVERLAP_WORDS = 100

def looks_like_heading(line):
    line = line.strip()

    if not line or len(line) > 140:
        return False

    patterns = [
        r"^(chapter|section|clause|annexure|annex|appendix)\b",
        r"^\d+(\.\d+)*\.?\s+[A-Z]",
        r"^[A-Z][A-Z\s,&()/:-]{4,}$",
    ]

    return any(re.search(p, line, re.IGNORECASE) for p in patterns)


def split_into_chunks(text):
    words = text.split()
    chunks = []
    step = CHUNK_WORDS - OVERLAP_WORDS

    for start in range(0, len(words), step):
        part = words[start:start + CHUNK_WORDS]
        if not part:
            break

        chunks.append(" ".join(part))

        if start + CHUNK_WORDS >= len(words):
            break

    return chunks


df = pd.read_csv(REGISTER, dtype=str).fillna("")
approved = df[df["review_status"] == "APPROVED"]

all_chunks = []

for _, row in approved.iterrows():
    json_path = EXTRACTED / f"{row['doc_id']}.json"

    if not json_path.exists():
        print("Missing extracted text:", json_path)
        continue

    pages = json.loads(json_path.read_text(encoding="utf-8"))

    for page in pages:
        text = page["text"].strip()
        if not text:
            continue

        # Track the latest heading observed in this document.
        # Headings spanning pages may need manual correction.
        lines = text.splitlines()
        heading = "Section not identified"

        for line in lines:
            if looks_like_heading(line):
                heading = line.strip()
                break

        for number, chunk in enumerate(split_into_chunks(text), start=1):
            all_chunks.append({
                "id": (
                    f"{row['doc_id']}-p{page['page']}-c{number}"
                ),
                "text": chunk,
                "metadata": {
                    "doc_id": str(row["doc_id"]),
                    "title": str(row["title"]),
                    "issuer": str(row["issuer"]),
                    "authority_level": str(row["authority_level"]),
                    "doc_type": str(row["doc_type"]),
                    "version": str(row["version"]),
                    "effective_from": str(row["effective_from"]),
                    "effective_to": str(row["effective_to"]),
                    "supersedes": str(row["supersedes"]),
                    "scope_programmes": str(row["scope_programmes"]),
                    "scope_batches": str(row["scope_batches"]),
                    "page": int(page["page"]),
                    "section": heading,
                    "provenance": str(row["provenance"]),
                },
            })

with OUTPUT.open("w", encoding="utf-8") as file:
    for chunk in all_chunks:
        file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print("Chunks created:", len(all_chunks))
print("Saved to:", OUTPUT)
