from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.mqtt_manager import MQTTManager

def test_get_all_devices_returns_devices(client: TestClient, mqtt_manager_mock: MQTTManager):
    mqtt_manager_mock.devices = {
        "esp32-1": {"online": True, "battery": 90, "timestamp": "2025-11-06T12:34:56Z"},
        "esp32-2": {"online": False, "battery": None, "timestamp": "2025-11-06T12:30:00Z"},
    }

    response = client.get("/devices/")

    assert response.status_code == 200
    data = response.json()

    assert "esp32-1" in data
    assert "esp32-2" in data
    assert data["esp32-1"]["online"] is True
    assert data["esp32-1"]["battery"] == 90
    assert "timestamp" in data["esp32-1"]
    assert data["esp32-2"]["online"] is False
    assert data["esp32-2"]["battery"] is None
    assert "timestamp" in data["esp32-2"]

def test_get_all_devices_empty(client: TestClient, mqtt_manager_mock: MQTTManager):
    mqtt_manager_mock.devices = {}

    response = client.get("/devices/")

    assert response.status_code == 200
    data = response.json()
    assert data == {}


def test_stop_device_success(client: TestClient, mqtt_manager_mock: MQTTManager):
    device_id = "dev_123"

    mqtt_manager_mock.is_device_online = MagicMock(return_value=True)
    mqtt_manager_mock.publish = MagicMock()

    response = client.post(f"/devices/{device_id}/stop")

    assert response.status_code == 200
    assert response.json() == {"detail": f"Comando de parada enviado para {device_id} com sucesso."}
    mqtt_manager_mock.publish.assert_called_once_with(f"devices/{device_id}/commands", "STOP", qos=1)

def test_stop_device_offline(client: TestClient, mqtt_manager_mock: MQTTManager):
    device_id = "dev_456"

    mqtt_manager_mock.is_device_online = MagicMock(return_value=False)
    mqtt_manager_mock.publish = MagicMock()

    response = client.post(f"/devices/{device_id}/stop")

    assert response.status_code == 400
    assert "não está online" in response.json()["detail"]
    mqtt_manager_mock.publish.assert_not_called()

def test_stop_device_publish_failure(client: TestClient, mqtt_manager_mock: MQTTManager):
    device_id = "dev_789"

    mqtt_manager_mock.is_device_online = MagicMock(return_value=True)
    mqtt_manager_mock.publish = MagicMock(side_effect=Exception("MQTT error"))

    response = client.post(f"/devices/{device_id}/stop")

    assert response.status_code == 500
    assert "Falha ao enviar comando MQTT" in response.json()["detail"]
    mqtt_manager_mock.publish.assert_called_once_with(f"devices/{device_id}/commands", "STOP", qos=1)
