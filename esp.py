import time
import json
import random
import re
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
DEVICE_ID = "esp32-123"
STATUS_TOPIC = f"devices/{DEVICE_ID}/status"
TRAJETO_TOPIC = f"devices/{DEVICE_ID}/trajeto"
COMMANDS_TOPIC = f"devices/{DEVICE_ID}/commands"

# Global trajeto ID
trajeto_id = None

def extract_trajeto_id(command: str):
    """Extracts the number after the last 'i' in the command string."""
    match = re.search(r"i(\d+)(?!.*i)", command)  # last occurrence of i followed by digits
    if match:
        return match.group(1)
    return None

def on_connect(client, userdata, flags, rc):
    print(f"Conectado com código {rc}")
    client.subscribe(COMMANDS_TOPIC)

def on_message(client, userdata, msg):
    global trajeto_id
    payload = msg.payload.decode().strip()
    print(f"[COMANDO RECEBIDO] {msg.topic}: {payload}")

    new_id = extract_trajeto_id(payload)
    if new_id:
        trajeto_id = new_id
        print(f"[TRAJETO ID ATUALIZADO] {trajeto_id}")
    else:
        print("[AVISO] Nenhum trajeto_id encontrado no comando.")

client = mqtt.Client(client_id=DEVICE_ID, clean_session=True)

# Last Will
lwt_payload = json.dumps({
    "online": False,
    "battery": None,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
})
client.will_set(STATUS_TOPIC, payload=lwt_payload, qos=1, retain=True)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

battery_level = 100
status_payload = {
    "online": True,
    "battery": battery_level,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
}
client.publish(STATUS_TOPIC, json.dumps(status_payload), qos=1, retain=True)
print(f"[STATUS PUBLISHED] {status_payload}")

try:
    while True:
        trajeto_payload = {
            "x": round(random.uniform(0, 10), 2),
            "y": round(random.uniform(0, 10), 2),
            "speed": round(random.uniform(0, 2), 2),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "trajeto_id": trajeto_id  # last received ID
        }
        client.publish(TRAJETO_TOPIC, json.dumps(trajeto_payload), qos=0, retain=False)
        print(f"[TRAJETO PUBLISHED] {trajeto_payload}")

        battery_level = max(battery_level - random.uniform(0.5, 1.5), 0)
        status_payload = {
            "online": True,
            "battery": round(battery_level, 2),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        client.publish(STATUS_TOPIC, json.dumps(status_payload), qos=1, retain=True)
        print(f"[STATUS PUBLISHED] {status_payload}")

        time.sleep(5)

except KeyboardInterrupt:
    offline_payload = {
        "online": False,
        "battery": round(battery_level, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    client.publish(STATUS_TOPIC, json.dumps(offline_payload), qos=1, retain=True)
    print(f"[STATUS OFFLINE PUBLISHED] {offline_payload}")
    client.loop_stop()
    client.disconnect()
