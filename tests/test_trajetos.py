from fastapi.testclient import TestClient
from app.models import TrajetoORM
from sqlalchemy.orm import Session

def test_create_trajeto(client: TestClient):
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

def test_get_trajeto_by_id(db_session: Session, client: TestClient):
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
    
    response = client.get(f"/trajetos/{id_trajeto}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["idTrajeto"] == id_trajeto
    assert data["comandosEnviados"] == "a1000da0001e"
    assert data["comandosExecutados"] == "a1000da0001e"
    assert data["status"] is True
    assert data["tempo"] == 42

def test_get_trajeto_not_found(client: TestClient):
    response = client.get("/trajetos/9999")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Trajeto não encontrado"

def test_all_endpoints(client: TestClient):
    trajeto = {"comandosEnviados": "test_command"}
    response = client.post("/trajetos/", json=trajeto)
    assert response.status_code == 201
    created_id = response.json()["idTrajeto"]
    
    response = client.get(f"/trajetos/{created_id}")
    assert response.status_code == 200
    assert response.json()["comandosEnviados"] == "test_command"
    
    response = client.get("/trajetos/")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    
    response = client.delete(f"/trajetos/{created_id}")
    assert response.status_code == 204
    
    response = client.get(f"/trajetos/{created_id}")
    assert response.status_code == 404


def test_delete_trajeto(db_session: Session, client: TestClient):
    """Deve excluir um trajeto existente e retornar status 204."""
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
    """Deve retornar 404 ao tentar deletar um trajeto inexistente."""
    response = client.delete("/trajetos/9999")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Trajeto não encontrado"

def test_cancelar_trajeto_success(db_session: Session, client: TestClient):
    """Deve cancelar um trajeto em andamento (status=None) e retornar 202."""
    trajeto = TrajetoORM(
        comandosEnviados="a1000da0001e",
        comandosExecutados=None,
        status=None,
        tempo=15
    )
    db_session.add(trajeto)
    db_session.commit()
    db_session.refresh(trajeto)

    response = client.post(f"/trajetos/{trajeto.idTrajeto}/cancelar")

    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == f"Trajeto {trajeto.idTrajeto} cancelado com sucesso."

    trajeto_atualizado = db_session.get(TrajetoORM, trajeto.idTrajeto)
    assert trajeto_atualizado.status is False


def test_cancelar_trajeto_not_found(client: TestClient):
    """Deve retornar 404 ao tentar cancelar um trajeto inexistente."""
    response = client.post("/trajetos/9999/cancelar")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Trajeto não encontrado"

def test_cancelar_trajeto_ja_cancelado(db_session: Session, client: TestClient):
    """Deve retornar 400 se o trajeto já estiver cancelado (status=False)."""
    trajeto = TrajetoORM(
        comandosEnviados="a1000da0001e",
        comandosExecutados=None,
        status=False,
        tempo=10
    )
    db_session.add(trajeto)
    db_session.commit()
    db_session.refresh(trajeto)

    response = client.post(f"/trajetos/{trajeto.idTrajeto}/cancelar")

    assert response.status_code == 400
    assert response.json()["detail"] == "Trajeto já foi cancelado anteriormente"


def test_cancelar_trajeto_concluido(db_session: Session, client: TestClient):
    """Deve retornar 400 se o trajeto já estiver concluído (status=True)."""
    trajeto = TrajetoORM(
        comandosEnviados="a1000da0001e",
        comandosExecutados="a1000da0001e",
        status=True,
        tempo=12
    )
    db_session.add(trajeto)
    db_session.commit()
    db_session.refresh(trajeto)

    response = client.post(f"/trajetos/{trajeto.idTrajeto}/cancelar")

    assert response.status_code == 400
    assert response.json()["detail"] == "Trajeto já foi concluído e não pode ser cancelado"