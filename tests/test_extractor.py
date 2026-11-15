from app.extractor import extract_profile


def test_extracts_profile_fields() -> None:
    text = """Ava Example
Email: ava.example@domain.com
Phone: (555) 123-4567
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
    assert profile["experience_years"] == 2.0
    assert profile["experience_years_detected"] is True
    assert profile["email"] == "ava.example@domain.com"
    assert profile["phone"] == "(555) 123-4567"
    assert "AI intern" in profile["experience"]
    assert "B.Tech" in profile["education"]
    assert "semantic search" in profile["projects"]


def test_experience_extraction_edge_cases() -> None:
    # 1. Unrelated numbers and calendar years should NOT be treated as employment experience
    text_with_years = """Charlie
Experience
Graduated college in 2024. Started coding in 2021. Built 4 projects.
"""
    prof1 = extract_profile(text_with_years)
    assert prof1["experience_years_detected"] is False
    assert prof1["experience_years"] is None

    # 2. Contextual experience mentioning "3+ years of experience"
    text_with_context = """Dana
Summary: Over 3.5 years of experience building Python APIs.
"""
    prof2 = extract_profile(text_with_context)
    assert prof2["experience_years_detected"] is True
    assert prof2["experience_years"] == 3.5
