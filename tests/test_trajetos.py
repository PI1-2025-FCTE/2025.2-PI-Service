import pytest
from fastapi.testclient import TestClient
from app.models import TrajetoORM
from app.services.trajetos import TrajetoService
from app.repositories.trajetos import TrajetoRepository
from app.exceptions.trajetos import TrajetoNotFoundException
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

def test_create_trajeto_success(client: TestClient, mqtt_manager_mock):
    device_id = "esp32-1"
    mqtt_manager_mock.is_device_online = MagicMock(return_value=True)
    mqtt_manager_mock.publish = MagicMock()

    trajeto = {"comandosEnviados": "a1000da0001e"}

    response = client.post(f"/trajetos/{device_id}", json=trajeto)

    assert response.status_code == 201
    data = response.json()
    assert data["comandosEnviados"] == trajeto["comandosEnviados"]
    assert "idTrajeto" in data
    mqtt_manager_mock.publish.assert_called_once()

def test_create_trajeto_device_offline(client: TestClient, mqtt_manager_mock):
    device_id = "esp32-2"
    mqtt_manager_mock.is_device_online = MagicMock(return_value=False)
    mqtt_manager_mock.publish = MagicMock()

    trajeto = {"comandosEnviados": "a1000da0001e"}

    response = client.post(f"/trajetos/{device_id}", json=trajeto)

    assert response.status_code == 400
    assert f"Dispositivo {device_id} não está online" in response.json()["detail"]
    mqtt_manager_mock.publish.assert_not_called()


def test_create_trajeto_publish_failure(client: TestClient, mqtt_manager_mock):
    device_id = "esp32-3"
    mqtt_manager_mock.is_device_online = MagicMock(return_value=True)
    mqtt_manager_mock.publish = MagicMock(side_effect=Exception("MQTT error"))

    trajeto = {"comandosEnviados": "a1000da0001e"}

    response = client.post(f"/trajetos/{device_id}", json=trajeto)

    assert response.status_code == 500
    assert "Falha ao enviar comandos MQTT" in response.json()["detail"]
    mqtt_manager_mock.publish.assert_called_once()

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

def test_update_trajeto_success(db_session: Session):
    trajeto = TrajetoORM(comandosEnviados="original", comandosExecutados=None, status=False, tempo=0)
    db_session.add(trajeto)
    db_session.commit()
    db_session.refresh(trajeto)
    
    repo = TrajetoRepository(db_session)
    service = TrajetoService(repo)

    update_data = {"comandosExecutados": "novo", "status": True, "tempo": 50}
    updated_trajeto = service.update_trajeto(trajeto.idTrajeto, update_data)

    assert updated_trajeto.comandosExecutados == "novo"
    assert updated_trajeto.status is True
    assert updated_trajeto.tempo == 50

def test_update_trajeto_partial_update(db_session: Session):
    trajeto = TrajetoORM(comandosEnviados="original", comandosExecutados=None, status=False, tempo=0)
    db_session.add(trajeto)
    db_session.commit()
    db_session.refresh(trajeto)
    
    repo = TrajetoRepository(db_session)
    service = TrajetoService(repo)

    update_data = {"status": True}
    updated_trajeto = service.update_trajeto(trajeto.idTrajeto, update_data)

    assert updated_trajeto.comandosEnviados == "original"
    assert updated_trajeto.status is True
    assert updated_trajeto.tempo == 0

def test_update_trajeto_not_found(db_session: Session):
    repo = TrajetoRepository(db_session)
    service = TrajetoService(repo)

    update_data = {"comandosEnviados": "novo"}

    with pytest.raises(TrajetoNotFoundException):
        service.update_trajeto(9999, update_data)