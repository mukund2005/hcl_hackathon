"""Compatibility helper. The live application uses authenticated POST /ingest."""
from urllib.parse import urlparse
from nitj_collector.app.ingestion import ingest_pdf
from pathlib import Path
import tempfile

TRUSTED_HOSTS = {"nitj.ac.in", "www.nitj.ac.in", "v1.nitj.ac.in", "ha.nitj.ac.in"}


def live_ingest(uploaded_file, metadata):
    content = uploaded_file.getvalue()
    parsed = urlparse(metadata.get("provenance", ""))
    if parsed.scheme != "https" or parsed.hostname not in TRUSTED_HOSTS:
        raise ValueError("An official NITJ provenance URL is required; it does not prove approval by itself.")
    if len(content) > 10 * 1024 * 1024 or not content.startswith(b"%PDF-"):
        raise ValueError("Provide a PDF no larger than 10 MB.")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "uploaded.pdf"
        path.write_bytes(content)
        return ingest_pdf(str(path), metadata)
