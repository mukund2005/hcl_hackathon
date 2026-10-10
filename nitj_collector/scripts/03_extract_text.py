"""Optional review export; production ingestion is scripts.setup_project."""
import json
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "nitj_collector" / "extracted_text"

if __name__ == "__main__":
    OUTPUT.mkdir(exist_ok=True)
    manifest = json.loads((ROOT / "nitj_collector" / "reviewed_sources.json").read_text())
    for entry in manifest:
        if not entry["file"].endswith(".pdf"):
            continue
        pages = [{"page":i+1,"text":p.extract_text() or ""} for i,p in enumerate(PdfReader(ROOT / entry["file"]).pages)]
        (OUTPUT / (entry["metadata"]["doc_id"] + ".json")).write_text(json.dumps(pages,indent=2),encoding="utf-8")
    print("Review exports saved. Image-only pages are not OCRed.")
