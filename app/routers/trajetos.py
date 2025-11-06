from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import TrajetoORM
from app.schemas import TrajetoResponse, TrajetoCreate
from app.dependencies import get_db, get_mqtt_client
from typing import List
from gmqtt import Client as MQTTClient

router = APIRouter(
    prefix="/trajetos",
    tags=["trajetos"]
)

@router.post("/{device_id}", response_model=TrajetoResponse, status_code=status.HTTP_201_CREATED)
async def create_trajeto(
    device_id: str,
    trajeto: TrajetoCreate,
    db: Session = Depends(get_db),
    client: MQTTClient = Depends(get_mqtt_client)
):
    if not trajeto or not trajeto.comandosEnviados:
        raise HTTPException(status_code=400, detail="Nenhum comando enviado")

    db_trajeto = TrajetoORM(comandosEnviados=trajeto.comandosEnviados)
    db.add(db_trajeto)
    db.commit()
    db.refresh(db_trajeto)

    topic = f"devices/{device_id}/commands"
    message = trajeto.comandosEnviados

    client.publish(topic, message)

    return db_trajeto


@router.get("/", response_model=List[TrajetoResponse])
async def list_trajetos(db: Session = Depends(get_db)):
    trajetos = db.query(TrajetoORM).all()
    return trajetos

@router.get("/{trajeto_id}", response_model=TrajetoResponse)
async def get_trajeto(trajeto_id: int, db: Session = Depends(get_db)):
    trajeto = db.get(TrajetoORM, trajeto_id)

    if not trajeto:
        raise HTTPException(status_code=404, detail="Trajeto não encontrado")
    
    return trajeto

@router.delete("/{trajeto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trajeto(trajeto_id: int, db: Session = Depends(get_db)):
    trajeto = db.get(TrajetoORM, trajeto_id)

    if not trajeto:
        raise HTTPException(status_code=404, detail="Trajeto não encontrado")

    db.delete(trajeto)
    db.commit()

@router.post("/{trajeto_id}/cancelar", status_code=status.HTTP_200_OK)
async def cancelar_trajetoria(trajeto_id: int, db: Session = Depends(get_db)):
    trajeto = db.get(TrajetoORM, trajeto_id)

    if not trajeto:
        raise HTTPException(status_code=404, detail="Trajeto não encontrado")

    if trajeto.status is False:
        raise HTTPException(
            status_code=400, 
            detail="Trajeto já foi cancelado anteriormente"
        )

    if trajeto.status is True:
        raise HTTPException(
            status_code=400, 
            detail="Trajeto já foi concluído e não pode ser cancelado"
        )

    # TODO: Enviar comando de parada para ESP via Websocket.
    trajeto.status = False
    db.add(trajeto)
    db.commit()
    db.refresh(trajeto)

    return {"detail": f"Trajeto {trajeto_id} cancelado com sucesso."}

