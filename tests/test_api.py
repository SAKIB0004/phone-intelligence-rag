import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database_connected" in data
    assert isinstance(data["total_indexed_phones"], int)


def test_list_phones_endpoint():
    response = client.get("/api/v1/phones/?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "phones" in data
    assert isinstance(data["phones"], list)


def test_get_phone_not_found():
    response = client.get("/api/v1/phones/NonExistentModel9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_chat_query_endpoint():
    payload = {
        "query": "What are the specs of the Galaxy S23?",
        "reset_history": True,
    }
    response = client.post("/api/v1/chat/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == payload["query"]
    assert len(data["response"]) > 20


def test_agent_review_endpoint():
    payload = {
        "phone_name": "Galaxy S23",
        "review_focus": "Compact flagship ergonomics and battery",
    }
    response = client.post("/api/v1/agents/review", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "technical_dossier" in data
    assert "final_review" in data
    assert len(data["final_review"]) > 50