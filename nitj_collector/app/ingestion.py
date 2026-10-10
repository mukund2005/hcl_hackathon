import hashlib
from pathlib import Path

import fitz
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DB_PATH = "./chroma_db"
COLLECTION_NAME = "nitj_university_documents"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=DB_PATH,
    embedding_function=embeddings,
    collection_metadata={"hnsw:space": "cosine"},
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)


def ingest_pdf(pdf_path: str, metadata: dict) -> dict:
    """Index an approved university PDF and its citation metadata."""

    required = [
        "doc_id",
        "title",
        "issuer",
        "authority_level",
        "version",
        "effective_from",
        "scope",
    ]

    missing = [key for key in required if key not in metadata]
    if missing:
        raise ValueError(f"Missing metadata: {missing}")

    path = Path(pdf_path)
    if not path.is_file() or path.suffix.lower() != ".pdf":
        raise ValueError("Provide an existing PDF file.")

    file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    page_documents = []

    with fitz.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if not text:
                continue

            page_documents.append(
                Document(
                    page_content=text,
                    metadata={
                        **metadata,
                        "page": page_number,
                        "file_name": path.name,
                        "file_sha256": file_hash,
                    },
                )
            )

    chunks = splitter.split_documents(page_documents)

    if not chunks:
        raise ValueError(
            "No extractable text found. The PDF may require OCR."
        )

    # Stable IDs allow the same document to be indexed again safely.
    ids = [
        hashlib.sha256(
            f"{metadata['doc_id']}:{file_hash}:{i}".encode()
        ).hexdigest()
        for i in range(len(chunks))
    ]

    # Remember old chunks so outdated versions can be removed
    # only after the new version has been indexed.
    old = vector_store.get(
        where={"doc_id": metadata["doc_id"]}
    )
    old_ids = old.get("ids", [])

    vector_store.add_documents(documents=chunks, ids=ids)

    obsolete_ids = [item for item in old_ids if item not in ids]
    if obsolete_ids:
        vector_store.delete(ids=obsolete_ids)

    return {
        "doc_id": metadata["doc_id"],
        "title": metadata["title"],
        "chunks_indexed": len(chunks),
        "file_sha256": file_hash,
        "status": "indexed",
    }