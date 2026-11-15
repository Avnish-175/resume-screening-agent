
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    ForeignKey,
    TIMESTAMP,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship

from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_title = Column(String(255), nullable=False)
    job_description = Column(LONGTEXT, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    screening_sessions = relationship(
        "ScreeningSession", back_populates="job"
    )


class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(30), nullable=True)
    skills = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    screening_results = relationship(
        "ScreeningResult", back_populates="candidate"
    )


class ScreeningSession(Base):
    __tablename__ = "screening_sessions"

    session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=False)
    total_candidates = Column(Integer, default=0)
    screened_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    job = relationship("Job", back_populates="screening_sessions")
    screening_results = relationship(
        "ScreeningResult", back_populates="session"
    )


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    result_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(
        Integer, ForeignKey("screening_sessions.session_id"), nullable=False
    )
    candidate_id = Column(
        Integer, ForeignKey("candidates.candidate_id"), nullable=False
    )

    semantic_score = Column(Numeric(6, 2), nullable=True)
    skill_score = Column(Numeric(6, 2), nullable=True)
    experience_score = Column(Numeric(6, 2), nullable=True)
    final_score = Column(Numeric(6, 2), nullable=True)
    candidate_rank = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "candidate_id",
            name="uq_session_candidate"
        ),
    )

    session = relationship(
        "ScreeningSession", back_populates="screening_results"
    )
    candidate = relationship(
        "Candidate", back_populates="screening_results"
    )
