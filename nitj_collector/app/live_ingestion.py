from pathlib import Path
from urllib.parse import urlparse
import hashlib
import tempfile

import fitz

from app.ingestion import ingest_pdf

MAX_SIZE_MB = 20
MAX_PAGES = 500

TRUSTED_HOSTS = {
    "nitj.ac.in",
    "www.nitj.ac.in",
    "v1.nitj.ac.in",
    "ha.nitj.ac.in",
}


def live_ingest(uploaded_file, metadata: dict) -> dict:
    # 1. Check filename and file size
    if not uploaded_file.name.lower().endswith(".pdf"):
        return {"status": "rejected", "reason": "Only PDF files are accepted."}

    pdf_bytes = uploaded_file.getvalue()

    if not pdf_bytes or len(pdf_bytes) > MAX_SIZE_MB * 1024 * 1024:
        return {"status": "rejected", "reason": "Empty file or size limit exceeded."}

    # 2. Check PDF signature
    if not pdf_bytes.startswith(b"%PDF-"):
        return {"status": "rejected", "reason": "Invalid PDF signature."}

    # 3. Check that the document is readable
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
            if pdf.is_encrypted:
                return {"status": "rejected", "reason": "Encrypted PDFs are not accepted."}

            if not 1 <= len(pdf) <= MAX_PAGES:
                return {"status": "rejected", "reason": "Invalid page count."}

            text = "\n".join(page.get_text("text") for page in pdf)

    except Exception:
        return {"status": "rejected", "reason": "The PDF is corrupt or unreadable."}

    if len(text.strip()) < 100:
        return {
            "status": "rejected",
            "reason": "Insufficient extractable text. OCR may be required.",
        }

    # 4. Validate required metadata
    required = [
        "doc_id", "title", "issuer", "authority_level",
        "version", "effective_from", "scope", "source_url",
    ]

    if any(
        key not in metadata or metadata[key] is None
        or not str(metadata[key]).strip()
        for key in required
    ):
        return {
            "status": "rejected",
            "reason": "Required document metadata is missing.",
        }

    # 5. Check source host. A host allowlist alone does not
    # prove that this exact document is officially approved.
    parsed = urlparse(metadata["source_url"])
    if (
        parsed.scheme != "https"
        or (parsed.hostname or "").lower() not in TRUSTED_HOSTS
    ):
        return {
            "status": "rejected",
            "reason": "Source URL is not on the trusted-domain allowlist.",
        }

    # 6. Pass the uploaded bytes to the existing ingestion function
    digest = hashlib.sha256(pdf_bytes).hexdigest()

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = Path(temp_dir) / "uploaded.pdf"
        pdf_path.write_bytes(pdf_bytes)

        safe_metadata = {
            **metadata,
            "file_sha256": digest,
            "approval_status": "APPROVED",
        }

        try:
            result = ingest_pdf(str(pdf_path), safe_metadata)
        except Exception as exc:
            return {
                "status": "failed",
                "reason": f"Indexing failed: {exc}",
            }

    return {
        "status": "approved",
        "reason": "Validation passed and document was indexed.",
        "result": result,
    }