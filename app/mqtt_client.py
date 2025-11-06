import os
import json
from typing import Dict
from gmqtt import Client as MQTTClient

MQTT_HOST: str = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT: int = int(os.getenv("MQTT_PORT", 1883))
CLIENT_ID: str = "fastapi_gmqtt_client"

devices: Dict[str, dict] = {}

mqtt_client: MQTTClient = MQTTClient(CLIENT_ID)

def on_connect(client: MQTTClient, flags: dict, rc: int, properties) -> None:
    print(f"[MQTT] Conectado: rc={rc}")
    client.subscribe("devices/+/status")
    client.subscribe("devices/+/trajeto")

def on_message(client: MQTTClient, topic: str, payload: bytes, qos: int, properties) -> None:
    payload_str: str = payload.decode()
    print(f"[MQTT] {topic}: {payload_str}")

    parts = topic.split("/")
    if len(parts) >= 3 and parts[0] == "devices":
        device_id: str = parts[1]
        category: str = parts[2]

        if category == "status":
            try:
                status_data: dict = json.loads(payload_str)
                devices[device_id] = status_data
                print(f"[STATE UPDATED] {device_id}: {status_data}")
            except json.JSONDecodeError:
                print(f"[ERROR] payload inválido: {payload_str}")
        elif category == "trajeto":
            print(f"[TRAJETO] {device_id}: {payload_str}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

async def mqtt_connect() -> None:
    await mqtt_client.connect(MQTT_HOST, MQTT_PORT)
    print("[MQTT] Cliente conectado")

async def mqtt_disconnect() -> None:
    await mqtt_client.disconnect()
    print("[MQTT] Cliente desconectado")
