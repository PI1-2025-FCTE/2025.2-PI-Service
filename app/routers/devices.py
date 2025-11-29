from fastapi import APIRouter, Depends, status, HTTPException
from app.dependencies import get_mqtt_manager, MQTTManager

router = APIRouter(
    prefix="/devices",
    tags=["devices"]
)

@router.get("/")
async def get_all_devices(mqtt_manager: MQTTManager = Depends(get_mqtt_manager)):
    return mqtt_manager.devices

@router.post("/{device_id}/stop", status_code=status.HTTP_200_OK)
async def stop_device(
    device_id: str,
    mqtt_manager: MQTTManager = Depends(get_mqtt_manager)
):
    """
    Envia comando de parada para um carrinho específico via MQTT.
    """
    if not mqtt_manager.is_device_online(device_id):
        print(mqtt_manager.devices)
        raise HTTPException(
            status_code=400,
            detail=f"Dispositivo {device_id} não está online"
        )

    topic = f"devices/{device_id}/commands"
    message = "STOP"

    try:
        mqtt_manager.publish(topic, message, qos=1)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao enviar comando MQTT para {device_id}: {e}"
        )

    return {"detail": f"Comando de parada enviado para {device_id} com sucesso."}