from app.ranker import rank_resumes


def test_rank_resumes_ordering() -> None:
    jd = "Seeking a Python NLP engineer with FastAPI, Machine Learning, and SQL experience."
    resumes = [
        ("strong_candidate.txt", "Alice\nSkills\nPython, NLP, FastAPI, Machine Learning, SQL\nExperience\n2 years in AI"),
        ("weak_candidate.txt", "Bob\nSkills\nReact, HTML, CSS\nExperience\n1 year in frontend"),
    ]
    rankings = rank_resumes(jd, resumes)
    assert len(rankings) == 2
    assert rankings[0]["candidate_name"] == "Alice"
    assert rankings[0]["rank"] == 1
    assert rankings[0]["final_score"] > rankings[1]["final_score"]
    assert rankings[0]["semantic_score"] > rankings[1]["semantic_score"]
