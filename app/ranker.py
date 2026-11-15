"""Semantic ranking with an explicit, readable explanation for each score."""
from __future__ import annotations
from functools import lru_cache
from typing import Any
from .config import MODEL_NAME
from .extractor import extract_profile


@lru_cache(maxsize=1)
def get_model() -> Any:
    """Load the model only when ranking is requested, keeping utility imports light."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def candidate_name(text: str, fallback: str) -> str:
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return first_line[:80] if 2 <= len(first_line) <= 80 else fallback.replace("_", " ").title()


def rank_resumes(job_description: str, resumes: list[tuple[str, str]]) -> list[dict]:
    """Rank resume text using semantic similarity (all-MiniLM-L6-v2) and explainable weighted scoring."""
    if not job_description.strip():
        raise ValueError("Job description is empty.")
    if not resumes:
        raise ValueError("At least one resume is required.")
    texts = [job_description] + [text for _, text in resumes]
    embeddings = get_model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
    jd_profile = extract_profile(job_description)
    jd_skills = set(jd_profile["skills"])
    jd_years = jd_profile.get("years_mentioned", 0.0)

    ranked = []
    for index, ((filename, text), embedding) in enumerate(zip(resumes, embeddings[1:])):
        profile = extract_profile(text)
        cosine_similarity = float(embeddings[0] @ embedding)
        # Semantic score scaled to 0-100
        semantic_score = round(max(0.0, cosine_similarity) * 100, 2)

        # Explainable skill match score (0-100)
        matched = sorted(jd_skills & set(profile["skills"]))
        missing = sorted(jd_skills - set(profile["skills"]))
        if jd_skills:
            skill_score = round((len(matched) / len(jd_skills)) * 100, 2)
        else:
            skill_score = 100.0 if profile["skills"] else 0.0

        # Experience score (0-100) based on ratio of candidate experience to JD requirement
        candidate_years = profile.get("experience_years")
        if candidate_years is not None:
            if jd_years > 0:
                experience_score = round(min(1.0, candidate_years / jd_years) * 100, 2)
            else:
                experience_score = 100.0
            exp_status = f"{candidate_years:g}+ years of experience detected."
        else:
            # If no reliable experience duration could be extracted, adopt a neutral baseline (50.0)
            # or neutral semantic-fallback to avoid falsely penalizing the candidate with zero.
            if profile.get("experience") != "Not explicitly detected":
                experience_score = 50.0
                exp_status = "Experience section present (exact duration not explicitly quantified; neutral baseline applied)."
            else:
                experience_score = 50.0
                exp_status = "Experience duration unavailable (neutral baseline 50.0 applied)."

        # Weighted final score: 60% semantic, 30% skills, 10% experience
        final_score = round(
            (0.60 * semantic_score) + (0.30 * skill_score) + (0.10 * experience_score),
            2
        )

        reasons = []
        if matched:
            reasons.append("Matched skills: " + ", ".join(matched[:6]))
        else:
            reasons.append("No exact vocabulary skill matches; score is based on semantic content.")
        reasons.append(exp_status)
        if profile["projects"] != "Not explicitly detected":
            reasons.append("Has a detected projects section.")

        ranked.append({
            "candidate_name": candidate_name(text, filename.rsplit(".", 1)[0]),
            "source_file": filename,
            "similarity_score": semantic_score,
            "semantic_score": semantic_score,
            "skill_score": skill_score,
            "experience_score": experience_score,
            "final_score": final_score,
            "cosine_similarity": round(cosine_similarity, 4),
            "matched_skills": matched,
            "missing_jd_skills": missing,
            "reasoning": " ".join(reasons),
            "extracted_profile": profile,
        })

    # Rank by weighted final score
    ranked.sort(key=lambda item: item["final_score"], reverse=True)
    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank
    return ranked
