from pathlib import Path
import pytest
from app.parsers import extract_text


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
