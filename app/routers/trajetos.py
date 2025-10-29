from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TrajetoORM
from app.schemas import TrajetoResponse, TrajetoCreate

router = APIRouter(
    prefix="/trajetos",
    tags=["trajetos"]
)

@router.post("/", response_model=TrajetoResponse, status_code=status.HTTP_201_CREATED)
def create_trajeto(trajeto: TrajetoCreate, db: Session = Depends(get_db)):
    db_trajeto = TrajetoORM(
        comandosEnviados=trajeto.comandosEnviados,
        comandosExecutados=trajeto.comandosExecutados,
        status=trajeto.status,
        tempo=trajeto.tempo
    )
    
    db.add(db_trajeto)
    db.commit()
    db.refresh(db_trajeto)
    
    return db_trajeto

@router.delete("/{trajeto_id}", status_code=204)
def delete_trajeto(trajeto_id: int, db: Session = Depends(get_db)):
    trajeto = db.get(TrajetoORM, trajeto_id)

    if not trajeto:
        raise HTTPException(status_code=404, detail="Trajeto não encontrado")

    db.delete(trajeto)
    db.commit()