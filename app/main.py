
"""FastAPI entry point with MySQL persistence."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.openapi.utils import get_openapi

from typing import Generator
from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .config import SUPPORTED_EXTENSIONS
from .parsers import extract_text
from .ranker import rank_resumes, get_model
from .database import SessionLocal, test_database_connection
from .models import Job, Candidate, ScreeningSession, ScreeningResult

app = FastAPI(
    title="Resume Screening Agent",
    version="2.0.0",
    description="AI-powered resume screening with MySQL persistence."
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    def fix_file_schema(schema):
        if isinstance(schema, dict):
            if "contentMediaType" in schema:
                schema.pop("contentMediaType")
                schema["format"] = "binary"

            for value in schema.values():
                fix_file_schema(value)

        elif isinstance(schema, list):
            for item in schema:
                fix_file_schema(item)

    fix_file_schema(openapi_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


def get_db() -> Generator[Session, None, None]:
    """Dependency to provide a transactional database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health() -> dict:
    """Check application health, live database connectivity, and Sentence Transformer readiness."""
    db_status = "connected"
    try:
        test_database_connection()
    except Exception:
        db_status = "disconnected"

    # Verify model readiness safely
    model_status = "ready"
    try:
        # Check if the model is cached/instantiated or can load without throwing
        m = get_model()
        if m is None:
            model_status = "not_loaded"
    except Exception:
        model_status = "failed_to_initialize"

    is_healthy = (db_status == "connected") and (model_status == "ready")
    return {
        "status": "ok" if is_healthy else "degraded",
        "database": db_status,
        "model_name": "all-MiniLM-L6-v2",
        "model_status": model_status,
    }


@app.post("/screen")
async def screen(
    job_description: UploadFile = File(..., description="Job description (.txt file)"),
    resumes: list[UploadFile] = File(..., description="List of resumes (.txt, .pdf, .docx)"),
    db: Session = Depends(get_db),
) -> JSONResponse:

    if not job_description.filename or Path(job_description.filename).suffix.lower() != ".txt":
        raise HTTPException(400, "Job description must be a .txt file.")

    if not resumes:
        raise HTTPException(400, "Upload at least one resume.")

    unsupported = [
        r.filename for r in resumes
        if Path(r.filename or "").suffix.lower() not in SUPPORTED_EXTENSIONS
    ]

    if unsupported:
        raise HTTPException(400, f"Unsupported resume types: {unsupported}")

    try:
        with TemporaryDirectory() as directory:
            root = Path(directory)

            jd_content = await job_description.read()
            if not jd_content.strip():
                raise HTTPException(400, "Job description file is empty.")

            jd_path = root / "job_description.txt"
            jd_path.write_bytes(jd_content)

            try:
                job_text = extract_text(jd_path)
            except Exception as e:
                raise HTTPException(400, f"Failed to extract text from job description: {e}")

            if not job_text.strip():
                raise HTTPException(400, "Job description text could not be extracted.")

            parsed = []
            for number, resume in enumerate(resumes):
                safe_name = Path(resume.filename or f"resume_{number}.txt").name
                content = await resume.read()
                if not content.strip():
                    continue  # Gracefully skip empty files

                resume_path = root / f"{number}_{safe_name}"
                resume_path.write_bytes(content)

                try:
                    text = extract_text(resume_path)
                except Exception:
                    # Gracefully handle corrupted files by skipping or providing empty text
                    continue

                if text.strip():
                    parsed.append((safe_name, text))

            if not parsed:
                raise HTTPException(400, "No valid or non-empty resume content could be extracted.")

            # Run the AI ranking pipeline
            rankings = rank_resumes(job_text, parsed)

            # Save job information
            job = Job(
                job_title=Path(job_description.filename).stem.replace("_", " ").title(),
                job_description=job_text,
            )
            db.add(job)
            db.flush()

            # Create a screening session
            screening_session = ScreeningSession(
                job_id=job.job_id,
                total_candidates=len(rankings),
            )
            db.add(screening_session)
            db.flush()

            # Save candidates and their screening results
            for item in rankings:
                profile = item["extracted_profile"]
                email = profile.get("email")
                normalized_email = email.strip().lower() if email else None

                candidate = None
                # Reuse existing candidate record if a reliable normalized email exists
                if normalized_email:
                    candidate = (
                        db.query(Candidate)
                        .filter(Candidate.email == normalized_email)
                        .first()
                    )

                if candidate:
                    # Update skills/experience/education if current screening discovered new info
                    if profile.get("skills"):
                        candidate.skills = json.dumps(profile["skills"])
                    if profile.get("education") != "Not explicitly detected":
                        candidate.education = profile["education"]
                    if profile.get("experience") != "Not explicitly detected":
                        candidate.experience = profile["experience"]
                    if profile.get("phone") and not candidate.phone:
                        candidate.phone = profile["phone"]
                else:
                    # Create a new candidate record
                    candidate = Candidate(
                        candidate_name=item["candidate_name"],
                        email=normalized_email,
                        phone=profile.get("phone"),
                        skills=json.dumps(profile["skills"]),
                        education=profile["education"],
                        experience=profile["experience"],
                    )
                    db.add(candidate)
                    db.flush()

                result = ScreeningResult(
                    session_id=screening_session.session_id,
                    candidate_id=candidate.candidate_id,
                    semantic_score=item["semantic_score"],
                    skill_score=item["skill_score"],
                    experience_score=item["experience_score"],
                    final_score=item["final_score"],
                    candidate_rank=item["rank"],
                )
                db.add(result)

            # Commit all database records together in a single transaction
            db.commit()

            return JSONResponse({
                "message": "Screening completed and saved successfully.",
                "job_id": job.job_id,
                "session_id": screening_session.session_id,
                "model": "all-MiniLM-L6-v2",
                "scoring_method": (
                    "Weighted explainable score: 60% semantic similarity (all-MiniLM-L6-v2 embeddings), "
                    "30% skill overlap, 10% experience match"
                ),
                "total_candidates": len(rankings),
                "top_candidates": rankings[:3],
                "rankings": rankings,
            })

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        # Return a safe, sanitized client error without leaking internal DB/SQL exception traces
        raise HTTPException(
            422,
            "Could not complete resume screening. Please ensure the uploaded files are valid and readable."
        )


@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)) -> list[dict]:
    """Retrieve all saved job descriptions."""
    jobs = db.query(Job).order_by(Job.job_id.desc()).all()
    return [
        {
            "job_id": j.job_id,
            "job_title": j.job_title,
            "job_description": j.job_description,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in jobs
    ]


@app.get("/screenings/{session_id}")
def get_screening_session(session_id: int, db: Session = Depends(get_db)) -> dict:
    """Retrieve a screening session and its ranked candidates."""
    session = db.query(ScreeningSession).filter(ScreeningSession.session_id == session_id).first()
    if not session:
        raise HTTPException(404, f"Screening session {session_id} not found.")

    results = (
        db.query(ScreeningResult, Candidate)
        .join(Candidate, ScreeningResult.candidate_id == Candidate.candidate_id)
        .filter(ScreeningResult.session_id == session_id)
        .order_by(ScreeningResult.candidate_rank.asc())
        .all()
    )

    ranked_candidates = []
    for res, cand in results:
        try:
            parsed_skills = json.loads(cand.skills) if cand.skills else []
        except Exception:
            parsed_skills = [cand.skills] if cand.skills else []

        ranked_candidates.append({
            "result_id": res.result_id,
            "candidate_id": cand.candidate_id,
            "candidate_name": cand.candidate_name,
            "email": cand.email,
            "phone": cand.phone,
            "skills": parsed_skills,
            "education": cand.education,
            "experience": cand.experience,
            "candidate_rank": res.candidate_rank,
            "semantic_score": float(res.semantic_score) if res.semantic_score is not None else None,
            "skill_score": float(res.skill_score) if res.skill_score is not None else None,
            "experience_score": float(res.experience_score) if res.experience_score is not None else None,
            "final_score": float(res.final_score) if res.final_score is not None else None,
        })

    return {
        "session_id": session.session_id,
        "job_id": session.job_id,
        "job_title": session.job.job_title if session.job else None,
        "total_candidates": session.total_candidates,
        "screened_at": session.screened_at.isoformat() if session.screened_at else None,
        "candidates": ranked_candidates,
    }


@app.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)) -> dict:
    """Retrieve candidate profile information and historical screening results."""
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not candidate:
        raise HTTPException(404, f"Candidate {candidate_id} not found.")

    try:
        parsed_skills = json.loads(candidate.skills) if candidate.skills else []
    except Exception:
        parsed_skills = [candidate.skills] if candidate.skills else []

    history = []
    for res in candidate.screening_results:
        history.append({
            "result_id": res.result_id,
            "session_id": res.session_id,
            "job_id": res.session.job_id if res.session else None,
            "job_title": res.session.job.job_title if res.session and res.session.job else None,
            "candidate_rank": res.candidate_rank,
            "semantic_score": float(res.semantic_score) if res.semantic_score is not None else None,
            "skill_score": float(res.skill_score) if res.skill_score is not None else None,
            "experience_score": float(res.experience_score) if res.experience_score is not None else None,
            "final_score": float(res.final_score) if res.final_score is not None else None,
            "screened_at": res.session.screened_at.isoformat() if res.session and res.session.screened_at else None,
        })

    return {
        "candidate_id": candidate.candidate_id,
        "candidate_name": candidate.candidate_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "skills": parsed_skills,
        "education": candidate.education,
        "experience": candidate.experience,
        "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
        "screening_history": history,
    }
