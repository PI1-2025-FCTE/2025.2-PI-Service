from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TrajetoORM
from app.schemas import TrajetoResponse, TrajetoCreate
from typing import List

router = APIRouter(
    prefix="/trajetos",
    tags=["trajetos"]
)

@router.post("/", response_model=TrajetoResponse, status_code=status.HTTP_201_CREATED)
def create_trajeto(trajeto: TrajetoCreate, db: Session = Depends(get_db)):
    db_trajeto = TrajetoORM(comandosEnviados=trajeto.comandosEnviados)
    
    db.add(db_trajeto)
    db.commit()
    db.refresh(db_trajeto)
    
    return db_trajeto

@router.get("/", response_model=List[TrajetoResponse])
def list_trajetos(db: Session = Depends(get_db)):
    trajetos = db.query(TrajetoORM).all()
    return trajetos

@router.get("/{trajeto_id}", response_model=TrajetoResponse)
def get_trajeto(trajeto_id: int, db: Session = Depends(get_db)):
    trajeto = db.get(TrajetoORM, trajeto_id)

    if not trajeto:
        raise HTTPException(status_code=404, detail="Trajeto não encontrado")
    
    return trajeto

@router.delete("/{trajeto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trajeto(trajeto_id: int, db: Session = Depends(get_db)):
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

