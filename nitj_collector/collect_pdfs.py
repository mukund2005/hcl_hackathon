from app.ingestion import ingest_pdf
from app.retrieval import search_documents

metadata = {
    "doc_id": "DOC-001",
    "title": "Official Academic Regulations",
    "issuer": "NIT Jalandhar",
    "authority_level": 1,
    "version": "2023",
    "effective_from": "VERIFY_FROM_OFFICIAL_DOCUMENT",
    "scope": "VERIFY_APPLICABILITY",
}

# Replace this with the path to your reviewed PDF.
result = ingest_pdf(
    "approved_pdfs/academic_regulations.pdf",
    metadata,
)
print(result)

results = search_documents(
    "What do the regulations say about attendance?",
    k=3,
)

for item in results:
    print("\nTitle:", item["title"])
    print("Page:", item["page"])
    print("Passage:", item["text"][:500])
    print("Distance:", item["distance"])