"""Safe text extraction and clean preprocessing for supported resume and job formats."""
import re
from pathlib import Path
from docx import Document
from pypdf import PdfReader


def clean_text(raw_text: str) -> str:
    """Preprocess and normalize text while preserving technical punctuation and semantics.
    
    - Normalizes inconsistent Windows/Unix line breaks (\r\n, \r -> \n).
    - Removes zero-width and non-printable control characters.
    - Condenses excessive blank lines (more than 2 consecutive newlines) to 2.
    - Collapses repeated horizontal spaces and tabs into a single space.
    - Preserves meaningful technical symbols like C++, C#, .NET, CI/CD, and hyphens.
    """
    if not raw_text:
        return ""

    # Normalize line breaks
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove zero-width characters and unusual Unicode control codes
    text = re.sub(r"[\u200b\u200c\u200d\uFEFF]", "", text)

    # Collapse multiple horizontal whitespaces (spaces, tabs) per line into one
    text = re.sub(r"[ \t]+", " ", text)

    # Clean up spaces at ends of lines
    text = re.sub(r" ?\n ?", "\n", text)

    # Collapse more than 2 consecutive linebreaks into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    raw = ""
    if suffix == ".txt":
        raw = path.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".docx":
        document = Document(path)
        raw = "\n".join(p.text for p in document.paragraphs)
    elif suffix == ".pdf":
        reader = PdfReader(str(path))
        raw = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return clean_text(raw)
