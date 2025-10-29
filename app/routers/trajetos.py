from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TrajetoORM

router = APIRouter(
    prefix="/trajetos",
    tags=["trajetos"]
)

@router.delete("/{trajeto_id}", status_code=204)
def delete_trajeto(trajeto_id: int, db: Session = Depends(get_db)):
    trajeto = db.get(TrajetoORM, trajeto_id)

    if not trajeto:
        raise HTTPException(status_code=404, detail="Trajeto não encontrado")

    db.delete(trajeto)
    db.commit()