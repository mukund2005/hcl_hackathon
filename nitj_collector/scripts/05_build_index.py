
# scripts/05_build_index.py

from pathlib import Path
import json

import chromadb
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction,
)

BASE = Path(__file__).resolve().parent.parent
CHUNKS_FILE = BASE / "extracted_text" / "chunks.jsonl"
DB_DIR = BASE / "chroma_db"
COLLECTION_NAME = "nitj_university_documents"

if not CHUNKS_FILE.exists():
    raise SystemExit("chunks.jsonl not found. Complete Step 5 first.")

chunks = []

with CHUNKS_FILE.open(encoding="utf-8") as file:
    for line in file:
        if line.strip():
            chunks.append(json.loads(line))

if not chunks:
    raise SystemExit("No chunks found. Check your PDFs and extraction.")

client = chromadb.PersistentClient(path=str(DB_DIR))

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function,
    metadata={"hnsw:space": "cosine"},
)

# Upsert allows the same chunk IDs to be updated on reruns.
BATCH_SIZE = 50

for start in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[start:start + BATCH_SIZE]

    collection.upsert(
        ids=[item["id"] for item in batch],
        documents=[item["text"] for item in batch],
        metadatas=[item["metadata"] for item in batch],
    )

print("Indexing complete.")
print("Chunks supplied:", len(chunks))
print("Chunks in ChromaDB:", collection.count())
print("Persistent database:", DB_DIR)
