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
)


def search_documents(
    question: str,
    k: int = 4,
    filters: dict | None = None,
) -> list[dict]:
    """Return relevant passages with their source metadata."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not 1 <= k <= 10:
        raise ValueError("k must be between 1 and 10.")

    results = vector_store.similarity_search_with_score(
        question,
        k=k,
        filter=filters,
    )

    passages = []

    for document, distance in results:
        metadata = document.metadata

        passages.append({
            "text": document.page_content,
            "doc_id": metadata.get("doc_id"),
            "title": metadata.get("title"),
            "issuer": metadata.get("issuer"),
            "page": metadata.get("page"),
            "section": metadata.get("section"),
            "version": metadata.get("version"),
            "effective_from": metadata.get("effective_from"),
            "authority_level": metadata.get("authority_level"),
            "scope": metadata.get("scope"),
            "distance": float(distance),
        })

    return passages