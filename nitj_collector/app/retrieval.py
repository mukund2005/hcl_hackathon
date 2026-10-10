"""Search Mukund's corpus through the same collection used by FastAPI."""
from app.config import Settings
from app.models import today_ist
from app.retrieval import KnowledgeBase
from app.storage import Database


def search_documents(question, k=4, filters=None):
    if not question.strip() or not 1 <= k <= 10:
        raise ValueError("Provide a question and k between 1 and 10.")
    filters = filters or {}
    settings = Settings.from_env()
    db = Database(settings.data_dir / "students.sqlite3")
    student = db.student(filters.get("student_id")) or {}
    return KnowledgeBase(db, settings).search(question, filters.get("as_of_date", str(today_ist())), student, k)
