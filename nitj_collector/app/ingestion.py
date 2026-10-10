"""Mukund's collector adapted to the final shared SQLite/Chroma store."""
from pathlib import Path
from app.config import Settings
from app.models import Source
from app.retrieval import KnowledgeBase
from app.storage import Database


def ingest_pdf(pdf_path: str, metadata: dict) -> dict:
    # Incomplete collector metadata is not automatically approved.
    source = Source.model_validate(metadata)
    settings = Settings.from_env()
    database = Database(settings.data_dir / "students.sqlite3")
    path = Path(pdf_path)
    if path.suffix.lower() != ".pdf":
        raise ValueError("Provide a PDF file.")
    return KnowledgeBase(database, settings).ingest(path.read_bytes(), path.name, source)
