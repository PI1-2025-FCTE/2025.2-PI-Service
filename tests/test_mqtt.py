import pytest
import json
from app.mqtt_manager import MQTTManager

@pytest.mark.asyncio
async def test_connect_calls_client_connect(mqtt_manager_mock: MQTTManager):
    await mqtt_manager_mock.connect("host.test", 1234)
    mqtt_manager_mock.client.connect.assert_called_once_with("host.test", 1234)

@pytest.mark.asyncio
async def test_disconnect_calls_client_disconnect(mqtt_manager_mock: MQTTManager):
    await mqtt_manager_mock.disconnect()
    mqtt_manager_mock.client.disconnect.assert_called_once_with()

def test_on_connect_subscribes_to_topics(mqtt_manager_mock: MQTTManager):
    mqtt_manager_mock.on_connect(mqtt_manager_mock.client, flags={}, rc=0, properties=None)
    mqtt_manager_mock.client.subscribe.assert_any_call("devices/+/status")
    mqtt_manager_mock.client.subscribe.assert_any_call("devices/+/trajeto")
    assert mqtt_manager_mock.client.subscribe.call_count == 2

def test_on_message_status_valid_json_updates_state(mqtt_manager_mock: MQTTManager):
    device_id = "dev_1"
    topic = f"devices/{device_id}/status"
    payload = json.dumps({"status": "online", "temp": 25}).encode()
    mqtt_manager_mock.on_message(mqtt_manager_mock.client, topic, payload, 0, None)
    assert mqtt_manager_mock.devices[device_id]["status"] == "online"
    assert mqtt_manager_mock.devices[device_id]["temp"] == 25

def test_on_message_status_invalid_json_does_not_crash(mqtt_manager_mock: MQTTManager):
    device_id = "dev_2"
    topic = f"devices/{device_id}/status"
    payload = b"{invalid_json"
    mqtt_manager_mock.on_message(mqtt_manager_mock.client, topic, payload, 0, None)
    assert device_id not in mqtt_manager_mock.devices

def test_on_message_trajeto_prints_message(mqtt_manager_mock: MQTTManager):
    device_id = "dev_3"
    topic = f"devices/{device_id}/trajeto"
    payload = b"trajeto test"
    mqtt_manager_mock.on_message(mqtt_manager_mock.client, topic, payload, 0, None)
    assert device_id not in mqtt_manager_mock.devices

def test_on_message_irrelevant_topic_does_nothing(mqtt_manager_mock: MQTTManager):
    mqtt_manager_mock.on_message(mqtt_manager_mock.client, "foo/bar/baz", b"{}", 0, None)
    assert mqtt_manager_mock.devices == {}

def test_on_message_payload_decode_error_does_not_crash(mqtt_manager_mock: MQTTManager):
    payload = b"\xff\xfe\x00"
    mqtt_manager_mock.on_message(mqtt_manager_mock.client, "devices/dev_err/status", payload, 0, None)
    assert "dev_err" not in mqtt_manager_mock.devices

@pytest.mark.parametrize(
    "device_id, state, expected",
    [
        ("dev_A", {"dev_A": {"online": True}}, True),
        ("dev_B", {"dev_B": {"online": False}}, False),
        ("dev_C", {"dev_C": {"battery": 30}}, False),
        ("dev_D", {}, False),
    ],
)
def test_is_device_online(mqtt_manager_mock: MQTTManager, device_id, state, expected):
    mqtt_manager_mock.devices = state
    assert mqtt_manager_mock.is_device_online(device_id) == expected

def test_publish_calls_client_publish(mqtt_manager_mock: MQTTManager):
    topic = "topic/test"
    message = "msg"
    qos = 1
    retain = True
    extra_kwargs = {"properties": {"foo": "bar"}}
    
    mqtt_manager_mock.publish(topic, message, qos=qos, retain=retain, **extra_kwargs)
    
    mqtt_manager_mock.client.publish.assert_called_once_with(
        topic, message, qos=qos, retain=retain, **extra_kwargs
    )
