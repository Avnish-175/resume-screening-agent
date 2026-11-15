from pathlib import Path
import pytest
from app.parsers import extract_text, clean_text


def test_clean_text_normalizations() -> None:
    raw = "  John   Doe  \r\n\r\n\r\n\r\nSkills:   C++,   CI/CD,   .NET  \t \n\n"
    cleaned = clean_text(raw)
    assert "John Doe" in cleaned
    assert "C++, CI/CD, .NET" in cleaned
    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned


def test_extract_text_txt(tmp_path: Path) -> None:
    txt_file = tmp_path / "resume.txt"
    txt_file.write_text("John Doe\nPython developer", encoding="utf-8")
    extracted = extract_text(txt_file)
    assert "John Doe" in extracted
    assert "Python developer" in extracted


def test_extract_text_unsupported(tmp_path: Path) -> None:
    bad_file = tmp_path / "resume.xyz"
    bad_file.write_text("Unsupported format", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(bad_file)
