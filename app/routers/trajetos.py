from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import TrajetoResponse, TrajetoCreate
from app.dependencies import get_db, get_mqtt_manager
from app.services.trajetos import TrajetoService
from app.repositories.trajetos import TrajetoRepository
from app.mqtt_manager import MQTTManager
from app.exceptions.trajetos import TrajetoNotFoundException
from typing import List

router = APIRouter(prefix="/trajetos", tags=["trajetos"])

@router.post("/{device_id}", response_model=TrajetoResponse, status_code=status.HTTP_201_CREATED)
async def create_trajeto(
    device_id: str,
    trajeto: TrajetoCreate,
    db: Session = Depends(get_db),
    mqtt_manager: MQTTManager = Depends(get_mqtt_manager)
):
    if not mqtt_manager.is_device_online(device_id):
        raise HTTPException(status_code=400, detail=f"Dispositivo {device_id} não está online")

    service = TrajetoService(TrajetoRepository(db))
    trajeto_obj = service.create_trajeto(trajeto.comandosEnviados)

    topic = f"devices/{device_id}/commands"
    message = f"{trajeto.comandosEnviados}i{trajeto_obj.idTrajeto}"

    try:
        mqtt_manager.publish(topic, message, qos=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao enviar comandos MQTT: {e}")

    return trajeto_obj

@router.get("/", response_model=List[TrajetoResponse])
async def list_trajetos(db: Session = Depends(get_db)):
    service = TrajetoService(TrajetoRepository(db))
    return service.list_trajetos()

@router.get("/{trajeto_id}", response_model=TrajetoResponse)
async def get_trajeto(trajeto_id: int, db: Session = Depends(get_db)):
    service = TrajetoService(TrajetoRepository(db))
    try:
        return service.get_trajeto(trajeto_id)
    except TrajetoNotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)

@router.delete("/{trajeto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trajeto(trajeto_id: int, db: Session = Depends(get_db)):
    service = TrajetoService(TrajetoRepository(db))
    try:
        service.delete_trajeto(trajeto_id)
    except TrajetoNotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
