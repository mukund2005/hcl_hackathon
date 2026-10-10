"""Optional chunk review using the same splitter as the final API."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from app.retrieval import split_document

if __name__ == "__main__":
    output = ROOT / "nitj_collector" / "extracted_text"
    output.mkdir(exist_ok=True)
    manifest = json.loads((ROOT / "nitj_collector" / "reviewed_sources.json").read_text())
    with (output / "chunks.jsonl").open("w",encoding="utf-8") as handle:
        for entry in manifest:
            if entry["metadata"]["synthetic"] == "Y":
                continue
            path = ROOT / entry["file"]
            for chunk in split_document(path.read_bytes(),path.name,entry["metadata"]["doc_id"],entry["metadata"].get("excluded_pages",[])):
                handle.write(json.dumps(chunk) + "\n")
    print("Chunk review written; use scripts.setup_project to index the shared store.")
