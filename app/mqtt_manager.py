import os
import json
from typing import Dict, Optional, Any
from gmqtt import Client as MQTTClient

MQTT_HOST: str = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT: int = int(os.getenv("MQTT_PORT", 1883))
CLIENT_ID: str = "fastapi_gmqtt_client"

class MQTTManager:
    devices: Dict[str, dict]

    def __init__(self, client_id: str = CLIENT_ID) -> None:
        self.devices = {}
        self.client: MQTTClient = MQTTClient(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    async def connect(self, host: str = MQTT_HOST, port: int = MQTT_PORT) -> None:
        """Conecta o cliente MQTT ao broker."""
        await self.client.connect(host, port)
        print("[MQTT] Cliente conectado")

    async def disconnect(self) -> None:
        """Desconecta o cliente MQTT do broker."""
        await self.client.disconnect()
        print("[MQTT] Cliente desconectado")

    def on_connect(
        self,
        client: MQTTClient,
        flags: Any,
        rc: int,
        properties: Optional[Any] = None
    ) -> None:
        """Callback chamado quando o cliente se conecta ao broker."""
        client.subscribe("devices/+/status")
        client.subscribe("devices/+/trajeto")
        print("[MQTT] on_connect")

    def on_message(
        self,
        client: MQTTClient,
        topic: str,
        payload: bytes,
        qos: int,
        properties: Optional[Any] = None
    ) -> None:
        """Callback chamado quando uma mensagem é recebida."""
        try:
            payload_str = payload.decode()
        except Exception:
            payload_str = ""
        parts = topic.split("/")
        if len(parts) >= 3 and parts[0] == "devices":
            device_id, category = parts[1], parts[2]
            if category == "status":
                try:
                    status_data = json.loads(payload_str)
                    self.devices[device_id] = status_data
                except json.JSONDecodeError:
                    print("[MQTT] payload inválido")
            elif category == "trajeto":
                print(f"[TRAJETO] {device_id}: {payload_str}")

    def is_device_online(self, device_id: str) -> bool:
        """Verifica se um dispositivo está online."""
        device = self.devices.get(device_id)
        return device is not None and device.get("online") is True

    def publish(
        self,
        topic: str,
        message: str,
        qos: int = 0,
        retain: bool = False,
        **kwargs: Any
    ):
        """Publica uma mensagem MQTT."""
        return self.client.publish(topic, message, qos=qos, retain=retain, **kwargs)

