from app.database import SessionLocal
from app.mqtt_client import mqtt_client

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_mqtt_client():
    return mqtt_client