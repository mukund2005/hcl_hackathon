"""Load the existing team's CSV records and Mukund's reviewed university corpus."""
import argparse
import csv
import json
from pathlib import Path
from app.config import Settings
from app.models import Source
from app.storage import Database
from app.retrieval import KnowledgeBase
from scripts.load_students import load

ROOT = Path(__file__).resolve().parents[1]


def setup(settings, include_synthetic=False):
    db = Database(settings.data_dir / "students.sqlite3")
    # Preserve an already populated database, including judge-loaded test students.
    if not db.rows("SELECT student_id FROM students LIMIT 1"):
        load(db, ROOT / "student_data")
    kb = KnowledgeBase(db, settings)
    manifest = json.loads((ROOT / "nitj_collector" / "reviewed_sources.json").read_text(encoding="utf-8"))
    outcomes = []
    for entry in manifest:
        if entry["metadata"]["synthetic"] == "Y" and not include_synthetic:
            continue
        path = ROOT / entry["file"]
        outcomes.append(kb.ingest(path.read_bytes(), path.name, Source(**entry["metadata"])))
    register = db.sources()
    with (settings.data_dir / "source_register.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(register[0]))
        writer.writeheader()
        writer.writerows(register)
    return {"students": len(db.rows("SELECT student_id FROM students")), "documents": outcomes,
            "synthetic_policy_demo": include_synthetic}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-synthetic", action="store_true", help="Two clearly fictional policies for conflict/placement demos.")
    args = parser.parse_args()
    print(json.dumps(setup(Settings.from_env(), args.include_synthetic), indent=2))
