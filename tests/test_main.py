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

def test_create_trajeto(client: TestClient, db_session: Session):
    trajeto = { "comandosEnviados": "a1000da0001e" }
    
    response = client.post("/trajetos/", json=trajeto)
    
    assert response.status_code == 201
    data = response.json()
    assert data["comandosEnviados"] == trajeto["comandosEnviados"]
    assert "idTrajeto" in data
    assert data["comandosExecutados"] is None
    assert data["status"] is None
    assert data["tempo"] is None

def test_create_trajeto_missing_field(client: TestClient):
    trajeto = {}
    
    response = client.post("/trajetos/", json=trajeto)
    
    assert response.status_code == 422

def test_list_trajetos_empty(client: TestClient):
    response = client.get("/trajetos/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_list_trajetos_with_data(db_session: Session, client: TestClient):
    trajeto1 = TrajetoORM(
        comandosEnviados="a1000da0001ed",
        comandosExecutados="a1000da0001ed",
        status=True,
        tempo=42
    )
    trajeto2 = TrajetoORM(
        comandosEnviados="dedededea2000da0003",
        comandosExecutados=None,
        status=False,
        tempo=30
    )
    
    db_session.add_all([trajeto1, trajeto2])
    db_session.commit()
    
    response = client.get("/trajetos/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["comandosEnviados"] == "a1000da0001ed"
    assert data[1]["comandosEnviados"] == "dedededea2000da0003"

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