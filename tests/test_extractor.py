from app.extractor import extract_profile


def test_extracts_profile_fields() -> None:
    text = """Ava Example
Skills
Python, NLP, FastAPI

Experience
2 years as an AI intern.

Education
B.Tech in Computer Science

Projects
Built a semantic search service.
"""
    profile = extract_profile(text)
    assert {"python", "nlp", "fastapi"}.issubset(profile["skills"])
    assert profile["years_mentioned"] == 2.0
    assert "AI intern" in profile["experience"]
    assert "B.Tech" in profile["education"]
    assert "semantic search" in profile["projects"]
