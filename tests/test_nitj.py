import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app
from app.storage import Database
from scripts.setup_project import setup


@pytest.fixture(scope="module")
def nitj(tmp_path_factory):
    settings = Settings(tmp_path_factory.mktemp("nitj"), True, "hash", "http://localhost:11434", "test", "admin")
    setup(settings, include_synthetic=True)
    with TestClient(create_app(settings)) as client:
        yield client, settings


def ask(client, question, date="2026-07-01", student="S1001"):
    response = client.post("/ask", headers={"X-Student-Id":student}, json={"question":question,"as_of_date":date})
    assert response.status_code == 200
    return response.json()


def test_official_pdf_threshold_and_citation(nitj):
    client, _ = nitj
    result = ask(client,"Am I eligible for the CS201 exam?")
    assert result["applied_rules"][0]["value"] == "75"
    assert any(c["doc_id"] == "NITJ-UG-2023" and c["section"] == "R8.1" and c["page"] == 6 for c in result["citations"])
    assert any("female-student exception" in note for note in result["assumptions"])


def test_synthetic_supersession_disclosed(nitj):
    result = ask(nitj[0],"Am I eligible for the CS201 exam?","2026-10-10")
    assert result["applied_rules"][0]["value"] == "80"
    assert any("Synthetic demonstration" in note for note in result["assumptions"])


def test_student_rows_unchanged_after_setup(nitj):
    _, settings = nitj
    db = Database(settings.data_dir / "students.sqlite3")
    before = db.rows("SELECT * FROM attendance ORDER BY student_id,course_code")
    setup(settings, include_synthetic=True)
    assert db.rows("SELECT * FROM attendance ORDER BY student_id,course_code") == before
    assert len(db.rows("SELECT * FROM students")) == 30
    assert len(db.sources()) == 5


def test_supplementary_cannot_be_decided_by_attendance(nitj):
    result = ask(nitj[0],"Am I eligible for the supplementary exam in CS201?",student="S1002")
    assert result["answer_type"] == "clarification_needed"
    assert "letter grade U" in result["answer"]
    assert result["tools_invoked"][0]["tool"] == "get_results"
    assert result["citations"][0]["section"] == "R14.2"


def test_expired_supplementary_notice_excluded(nitj):
    client, _ = nitj
    result = ask(client,"How do I register for the supplementary examination?", "2026-10-10")
    assert all(c["doc_id"] != "NITJ-SUPP-JAN-2026" for c in result["citations"])


def test_course_names_are_resolved_from_database(nitj):
    db = Database(nitj[1].data_dir / "students.sqlite3")
    course = db.rows("SELECT course_name FROM courses WHERE course_code='CS201'")[0]["course_name"]
    result = ask(nitj[0], "What is my attendance in " + course + "?")
    assert json.loads(result["answer"])["course_code"] == "CS201"


def test_notice_fee_context_is_not_lost_at_chunk_boundary(nitj):
    client, settings = nitj
    db = Database(settings.data_dir / "students.sqlite3")
    student = db.student("S1001")
    from app.retrieval import KnowledgeBase
    passages = KnowledgeBase(db,settings).search("January supplementary registration fee", "2026-01-03",student,10)
    notice = [p for p in passages if p["doc_id"] == "NITJ-SUPP-JAN-2026"]
    assert notice and "1000" in notice[0]["text"]


def test_appendix_does_not_inherit_unrelated_clause_number(nitj):
    db = Database(nitj[1].data_dir / "students.sqlite3")
    assert not db.rows("SELECT chunk_id FROM chunks WHERE doc_id='NITJ-UG-2023' AND page=22 AND section='R25.3'")


def test_official_only_has_no_fictional_placement_rule(tmp_path):
    settings = Settings(tmp_path,True,"hash","http://localhost:11434","test","")
    setup(settings)
    with TestClient(create_app(settings)) as client:
        assert ask(client,"Am I eligible for placement?")["answer_type"] == "not_found"
