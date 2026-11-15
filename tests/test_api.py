from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "database" in data
    assert "model_status" in data
    assert data["model_name"] == "all-MiniLM-L6-v2"


def test_missing_ids_404() -> None:
    r_sess = client.get("/screenings/9999999")
    assert r_sess.status_code == 404
    assert "not found" in r_sess.json()["detail"]

    r_cand = client.get("/candidates/9999999")
    assert r_cand.status_code == 404
    assert "not found" in r_cand.json()["detail"]


def test_screen_invalid_jd_type() -> None:
    response = client.post(
        "/screen",
        files=[
            ("job_description", ("job.pdf", b"fake content", "application/pdf")),
            ("resumes", ("resume.txt", b"Alice Python", "text/plain")),
        ],
    )
    assert response.status_code == 400
    assert "Job description must be a .txt file" in response.text


def test_screen_unsupported_resume_type() -> None:
    response = client.post(
        "/screen",
        files=[
            ("job_description", ("job.txt", b"Python NLP developer", "text/plain")),
            ("resumes", ("resume.png", b"fake binary", "image/png")),
        ],
    )
    assert response.status_code == 400
    assert "Unsupported resume types" in response.text


def test_screen_empty_resumes_list() -> None:
    response = client.post(
        "/screen",
        files=[
            ("job_description", ("job.txt", b"Python NLP developer", "text/plain")),
        ],
    )
    assert response.status_code == 422  # FastAPI validation error for missing field
