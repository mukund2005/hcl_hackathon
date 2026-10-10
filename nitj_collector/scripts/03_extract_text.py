
# scripts/03_extract_text.py

from pathlib import Path
import json
import pandas as pd
import fitz

BASE = Path(__file__).resolve().parent.parent
REGISTER = BASE / "source_register.csv"
OUTPUT = BASE / "extracted_text"
OUTPUT.mkdir(exist_ok=True)

df = pd.read_csv(REGISTER, dtype=str).fillna("")
approved = df[df["review_status"] == "APPROVED"]

if approved.empty:
    raise SystemExit("No approved PDFs. Complete Step 3 first.")

ocr_report = []

for _, row in approved.iterrows():
    pdf_path = BASE / row["local_file"]

    if not pdf_path.exists():
        print("Missing:", pdf_path)
        continue

    pages = []

    with fitz.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf):
            text = page.get_text("text").strip()

            pages.append({
                "doc_id": row["doc_id"],
                "title": row["title"],
                "page": page_index + 1,
                "text": text,
            })

            # Heuristic: flag pages with little or no text.
            if len(text) < 40:
                ocr_report.append({
                    "doc_id": row["doc_id"],
                    "title": row["title"],
                    "page": page_index + 1,
                    "characters_extracted": len(text),
                    "action": "CHECK_FOR_OCR",
                })

    output_file = OUTPUT / f"{row['doc_id']}.json"
    output_file.write_text(
        json.dumps(pages, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        f"Extracted {len(pages)} pages from {row['title']} "
        f"-> {output_file.name}"
    )

pd.DataFrame(ocr_report).to_csv(
    OUTPUT / "ocr_review.csv", index=False
)

print("\nOCR review report:", OUTPUT / "ocr_review.csv")
