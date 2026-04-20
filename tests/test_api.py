from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from snuffer.api import app
from snuffer.models import Chunk, SnufferResult

client = TestClient(app)

CLEAN_TEXT = "This is a safe document about cooking. It has no injection attempts whatsoever."

_EMPTY_RESULT = SnufferResult(
    warnings=[],
    chunks=[Chunk(text=CLEAN_TEXT, begin=0, end=len(CLEAN_TEXT), index=0)],
    normalized_text=CLEAN_TEXT,
    original_text=CLEAN_TEXT,
)

_FILTER_OUTPUT = {
    "cleaned_text": CLEAN_TEXT,
    "error": None,
    "report": {
        "removed_chunks": 0,
        "total_chunks": 1,
        "warnings": 0,
        "severity": {"CLEARLY_MALICIOUS": 0, "SUSPICIOUS": 0, "CAUTION": 0},
    },
}


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_review_clean_text() -> None:
    with patch("snuffer.api.run_review", new=AsyncMock(return_value=_EMPTY_RESULT)):
        resp = client.post("/review", json={"text": CLEAN_TEXT})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/plain")
    body = resp.text
    assert "# Snuffer Report" in body


def test_filter_clean_text() -> None:
    with patch("snuffer.api.run_filter", new=AsyncMock(return_value=_FILTER_OUTPUT)):
        resp = client.post("/filter", json={"text": CLEAN_TEXT})
    assert resp.status_code == 200
    data = resp.json()
    assert "cleaned_text" in data


def test_review_invalid_body() -> None:
    resp = client.post("/review", json={})
    assert resp.status_code == 422


def test_filter_invalid_body() -> None:
    resp = client.post("/filter", json={})
    assert resp.status_code == 422
