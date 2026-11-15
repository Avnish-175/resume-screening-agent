from pathlib import Path
import pytest
from app.service import screen_folder


def test_requires_txt_job_description(tmp_path: Path) -> None:
    resume_dir = tmp_path / "resumes"
    resume_dir.mkdir()
    with pytest.raises(ValueError, match=".txt"):
        screen_folder(tmp_path / "job_description.pdf", resume_dir)


def test_requires_existing_resume_directory(tmp_path: Path) -> None:
    jd_path = tmp_path / "job_description.txt"
    jd_path.write_text("Python NLP", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        screen_folder(jd_path, tmp_path / "missing")
