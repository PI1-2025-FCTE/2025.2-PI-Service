from fastapi.testclient import TestClient
from app.models import TrajetoORM
from sqlalchemy.orm import Session

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

def test_delete_trajeto(db_session: Session, client: TestClient):
    trajeto = TrajetoORM(
        comandosEnviados="a1000da0001e",
        comandosExecutados="a1000da0001e",
        status=True,
        tempo=42
    )

    db_session.add(trajeto)
    db_session.commit()
    db_session.refresh(trajeto)
    
    id_trajeto = trajeto.idTrajeto

    response = client.delete(f"/trajetos/{id_trajeto}")

    assert response.status_code == 204

    item_deletado = db_session.get(TrajetoORM, id_trajeto)
    assert item_deletado is None

def test_delete_trajeto_not_found(client: TestClient):
    response = client.delete("/trajetos/9999")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Trajeto não encontrado"