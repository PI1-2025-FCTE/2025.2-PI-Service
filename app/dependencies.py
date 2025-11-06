from app.database import SessionLocal
from app.mqtt_manager import MQTTManager

mqtt_manager: MQTTManager = MQTTManager()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mqtt_manager() -> MQTTManager:
    return mqtt_manager