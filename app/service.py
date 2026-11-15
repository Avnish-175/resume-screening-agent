from __future__ import annotations
import csv
import json
from pathlib import Path
from .config import SUPPORTED_EXTENSIONS
from .parsers import extract_text
from .ranker import rank_resumes


def screen_folder(jd_path: Path, resumes_dir: Path) -> dict:
    if jd_path.suffix.lower() != ".txt":
        raise ValueError("Job description must be a .txt file.")
    if not jd_path.is_file():
        raise FileNotFoundError(f"Job description not found: {jd_path}")
    if not resumes_dir.is_dir():
        raise NotADirectoryError(f"Resume directory not found: {resumes_dir}")
    jd_text = extract_text(jd_path)
    files = sorted(p for p in resumes_dir.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS)
    if not files:
        raise ValueError("No PDF, DOCX, or TXT resumes found.")
    resumes = [(p.name, extract_text(p)) for p in files]
    rankings = rank_resumes(jd_text, resumes)
    return {
        "model": "all-MiniLM-L6-v2",
        "scoring_method": "cosine similarity of L2-normalized Sentence Transformer embeddings",
        "job_description_file": jd_path.name,
        "total_candidates": len(rankings),
        "top_candidates": rankings[:3],
        "rankings": rankings,
    }


def write_outputs(result: dict, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path, csv_path = output_dir / "ranked_candidates.json", output_dir / "ranked_candidates.csv"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rank",
                "candidate_name",
                "source_file",
                "final_score",
                "similarity_score",
                "skill_score",
                "experience_score",
                "cosine_similarity",
                "matched_skills",
                "missing_jd_skills",
                "reasoning",
            ]
        )
        writer.writeheader()
        for item in result["rankings"]:
            writer.writerow({
                key: ", ".join(value) if isinstance(value, list) else value
                for key, value in item.items()
                if key in writer.fieldnames
            })
    return json_path, csv_path
