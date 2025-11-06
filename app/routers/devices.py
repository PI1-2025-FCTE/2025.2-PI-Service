from fastapi import APIRouter
from app.mqtt_client import devices

router = APIRouter(
    prefix="/devices",
    tags=["devices"]
)

@router.get("/")
async def get_all_devices():
    return devices