from fastapi.testclient import TestClient

def test_get_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "<h1>WebSocket Chat</h1>" in response.text

def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
