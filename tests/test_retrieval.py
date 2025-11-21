import pytest
from backend.services.vector_store import retrieve_top_k


@pytest.mark.integration
def test_retrieve_top_k_returns_expected_fields(monkeypatch):
    """Mock Pinecone index.query to verify return formatting."""

    class FakeIndex:
        def query(self, vector, top_k, include_metadata):
            return {
                "matches": [
                    {"id": "chunk_1", "score": 0.92, "metadata": {"text": "BMW iX sales increased 30%."}},
                    {"id": "chunk_2", "score": 0.88, "metadata": {"text": "BMW 3 Series led Europe."}}
                ]
            }

    monkeypatch.setattr("backend.services.vector_store.index", FakeIndex())

    fake_vector = [0.1] * 1536
    results = retrieve_top_k(fake_vector, top_k=2)

    assert isinstance(results, list)
    assert len(results) == 2
    for r in results:
        assert "id" in r and "text" in r and "score" in r
        assert isinstance(r["text"], str)
