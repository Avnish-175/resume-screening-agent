import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Job, Candidate, ScreeningSession, ScreeningResult


def test_sqlite_model_relationships() -> None:
    # Use SQLite in-memory engine to safely test models and relationships without touching production MySQL
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    try:
        # Create Job
        job = Job(job_title="ML Engineer", job_description="Python NLP")
        db.add(job)
        db.flush()

        # Create Candidate
        candidate = Candidate(
            candidate_name="Alice Smith",
            email="alice@example.com",
            phone="1234567890",
            skills='["python", "fastapi"]',
            education="B.S.",
            experience="2 years",
        )
        db.add(candidate)
        db.flush()

        # Create Session
        session = ScreeningSession(job_id=job.job_id, total_candidates=1)
        db.add(session)
        db.flush()

        # Create Result
        result = ScreeningResult(
            session_id=session.session_id,
            candidate_id=candidate.candidate_id,
            semantic_score=75.50,
            skill_score=80.00,
            experience_score=66.67,
            final_score=76.00,
            candidate_rank=1,
        )
        db.add(result)
        db.commit()

        # Verify relationships
        reloaded_job = db.query(Job).filter(Job.job_id == job.job_id).first()
        assert len(reloaded_job.screening_sessions) == 1

        reloaded_session = reloaded_job.screening_sessions[0]
        assert reloaded_session.job.job_title == "ML Engineer"
        assert len(reloaded_session.screening_results) == 1

        reloaded_candidate = db.query(Candidate).filter(Candidate.email == "alice@example.com").first()
        assert len(reloaded_candidate.screening_results) == 1
        assert reloaded_candidate.screening_results[0].session_id == session.session_id

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
