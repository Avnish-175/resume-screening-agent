"""Safe text extraction for the three supported resume formats."""
from pathlib import Path
from docx import Document
from pypdf import PdfReader


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".docx":
        document = Document(path)
        return "\n".join(p.text for p in document.paragraphs)
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError(f"Unsupported file type: {suffix}")
