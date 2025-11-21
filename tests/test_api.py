import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_healthcheck():
    """Ensure root endpoint returns status OK."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_ask_minimal(monkeypatch):
    """Mock internal calls to test API layer wiring only."""

    def fake_get_query_embedding(query):
        return [0.1] * 1536

    def fake_retrieve_top_k(embedding, top_k=5):
        return [{"id": "chunk_1", "text": "BMW X5 sales grew 20% in 2022.", "score": 0.9}]

    def fake_generate_answer(model_id, question, context):
        return "The BMW X5 had the highest sales in 2022."

    monkeypatch.setattr("backend.main.get_query_embedding", fake_get_query_embedding)
    monkeypatch.setattr("backend.main.retrieve_top_k", fake_retrieve_top_k)
    monkeypatch.setattr("backend.main.generate_answer", fake_generate_answer)

    payload = {"query": "Which BMW model had the highest sales in 2022?", "model": "claude-3-sonnet", "k": 3}
    response = client.post("/api/ask", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "matches" in data
    assert data["model"] == "claude-3-sonnet"
