from sqlalchemy.orm import Session
from app.models import TrajetoORM
from app.exceptions.trajetos import TrajetoNotFoundException

class TrajetoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, comandos_enviados: str) -> TrajetoORM:
        trajeto = TrajetoORM(comandosEnviados=comandos_enviados)
        self.db.add(trajeto)
        self.db.commit()
        self.db.refresh(trajeto)
        return trajeto

    def update(self, trajeto_id: int, update_data: dict) -> TrajetoORM:
        trajeto = self.get(trajeto_id)
        for key, value in update_data.items():
            setattr(trajeto, key, value)
        self.db.commit()
        self.db.refresh(trajeto)
        return trajeto

    def get(self, trajeto_id: int) -> TrajetoORM:
        trajeto = self.db.get(TrajetoORM, trajeto_id)

        if not trajeto:
            raise TrajetoNotFoundException()
        
        return trajeto

    def list_all(self) -> list[TrajetoORM]:
        return self.db.query(TrajetoORM).all()

    def delete(self, trajeto_id: int) -> None:
        trajeto = self.get(trajeto_id)
        self.db.delete(trajeto)
        self.db.commit()
