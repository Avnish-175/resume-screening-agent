import numpy as np
import pytest
from app.ranker import rank_resumes, get_model


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
    # Check that matched skills and missing skills are explicitly present in reasons
    assert "Matched skills" in rankings[0]["reasoning"]
    assert "Missing required skills" in rankings[1]["reasoning"]


def test_embedding_dimensions_and_l2_normalization() -> None:
    model = get_model()
    text = ["Senior Python NLP Engineer"]
    emb = model.encode(text, normalize_embeddings=True)
    assert emb.shape == (1, 384)
    # Norm of L2 normalized vector should be approximately 1.0
    norm = np.linalg.norm(emb[0])
    assert pytest.approx(norm, rel=1e-5) == 1.0


def test_cosine_similarity_via_dot_product() -> None:
    model = get_model()
    t1 = "Machine Learning classification using PyTorch"
    t2 = "Deep Learning neural networks using PyTorch"
    t3 = "Cooking Italian pizza recipe with mozzarella"

    embs = model.encode([t1, t2, t3], normalize_embeddings=True)
    # Cosine similarity is the dot product of L2-normalized embeddings
    sim_related = float(np.dot(embs[0], embs[1]))
    sim_unrelated = float(np.dot(embs[0], embs[2]))

    assert sim_related > sim_unrelated
    assert sim_related > 0.5
    assert sim_unrelated < 0.3


def test_rank_resumes_empty_inputs() -> None:
    with pytest.raises(ValueError, match="Job description is empty"):
        rank_resumes("", [("r.txt", "Alice")])

    with pytest.raises(ValueError, match="At least one resume is required"):
        rank_resumes("Valid JD", [])


def test_score_components_weighting() -> None:
    jd = "Python engineer with SQL"
    resumes = [("c.txt", "Candidate C\nSkills: Python, SQL\nExperience: 2 years")]
    rankings = rank_resumes(jd, resumes)
    cand = rankings[0]
    expected_final = round(
        (0.60 * cand["semantic_score"]) + (0.30 * cand["skill_score"]) + (0.10 * cand["experience_score"]),
        2
    )
    assert cand["final_score"] == expected_final

