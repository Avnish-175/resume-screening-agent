"""Transparent rule-based profile extraction used alongside semantic ranking."""
import re
from .config import SKILL_VOCABULARY


def _section(text: str, labels: list[str]) -> str:
    pattern = r"(?ims)^\s*(?:" + "|".join(map(re.escape, labels)) + r")\s*:?\s*$\n?(.*?)(?=^\s*[A-Z][A-Za-z /&-]{2,}\s*:?\s*$|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def _extract_years_of_experience(text: str, experience_section: str) -> tuple[float | None, str]:
    """Safely extract years of experience from experience context or section.
    
    Returns a tuple of (years_or_none, extraction_method).
    - If clearly detected in the experience section or experience context, returns (years, 'detected')
    - If no reliable experience can be detected, returns (None, 'unavailable')
    """
    # Pattern to match numbers associated with years of experience / employment
    # e.g., '2 years', '1.5 yrs', '3+ years', '1 year'
    years_pattern = r"(?<!\d)(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+(?:professional\s+|work\s+|relevant\s+)?experience)?"

    # First, look strictly inside the extracted experience section if available
    if experience_section and experience_section != "Not explicitly detected":
        matches = re.findall(years_pattern, experience_section.lower())
        if matches:
            return max(float(y) for y in matches), "experience_section"

    # Second, search the full text with strict experience keywords context
    # e.g. "X years of experience", "experience: X years", "worked for X years"
    context_pattern = (
        r"(?:(?:experience|employment|worked|career)\s*(?:[:\-\–]|for|of)?\s*(?:about|over|around|approximately)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?))"
        r"|"
        r"(?:(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:professional|work|industry|relevant|hands-on)?\s*experience)"
    )
    context_matches = re.findall(context_pattern, text.lower())
    years_found = []
    for g1, g2 in context_matches:
        if g1:
            years_found.append(float(g1))
        if g2:
            years_found.append(float(g2))

    if years_found:
        # Cap realistic single-candidate entry to 50 to avoid phone/year confusion
        filtered = [y for y in years_found if 0.1 <= y <= 50.0]
        if filtered:
            return max(filtered), "contextual"

    return None, "unavailable"


def extract_profile(text: str) -> dict:
    normalized = text.lower()
    skills = sorted(skill for skill in SKILL_VOCABULARY if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", normalized))
    experience = _section(text, ["experience", "work experience", "professional experience", "employment"])
    education = _section(text, ["education", "academic background"])
    projects = _section(text, ["projects", "project experience", "selected projects"])

    years, method = _extract_years_of_experience(text, experience)

    # Extract email and phone if present
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
    phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", text)

    return {
        "skills": skills,
        "experience": experience or "Not explicitly detected",
        "education": education or "Not explicitly detected",
        "projects": projects or "Not explicitly detected",
        "years_mentioned": years if years is not None else 0.0,
        "experience_years_detected": years is not None,
        "experience_years": years,
        "experience_detection_method": method,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
    }
