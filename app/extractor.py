"""Transparent rule-based profile extraction used alongside semantic ranking."""
import re
from .config import SKILL_VOCABULARY


def _section(text: str, labels: list[str]) -> str:
    pattern = r"(?ims)^\s*(?:" + "|".join(map(re.escape, labels)) + r")\s*:?\s*$\n?(.*?)(?=^\s*[A-Z][A-Za-z /&-]{2,}\s*:?\s*$|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def extract_profile(text: str) -> dict:
    normalized = text.lower()
    skills = sorted(skill for skill in SKILL_VOCABULARY if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", normalized))
    experience = _section(text, ["experience", "work experience", "professional experience", "employment"])
    education = _section(text, ["education", "academic background"])
    projects = _section(text, ["projects", "project experience", "selected projects"])
    years = re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)", normalized)

    # Extract email and phone if present
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
    phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", text)

    return {
        "skills": skills,
        "experience": experience or "Not explicitly detected",
        "education": education or "Not explicitly detected",
        "projects": projects or "Not explicitly detected",
        "years_mentioned": max((float(y) for y in years), default=0.0),
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
    }
