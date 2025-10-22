from app.database import Base
from sqlalchemy import Boolean, Column, Integer, Text

class TrajetoORM(Base):
    __tablename__ = "trajeto"

    idTrajeto = Column(Integer, primary_key=True, index=True)
    comandosEnviados = Column(Text, nullable=False)
    comandosExecutados = Column(Text)
    status = Column(Boolean)
    tempo = Column(Integer, nullable=False)