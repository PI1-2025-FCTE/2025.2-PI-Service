from app.models import TrajetoORM
from sqlalchemy.orm import Session

def test_trajeto_model_creation(db_session: Session):
    """Criar trajeto com todos os campos"""
    trajeto = TrajetoORM(
        comandosEnviados="a1000da0001e",
        comandosExecutados="a1000da0001e",
        status=True,
        tempo=42
    )
    
    db_session.add(trajeto)
    db_session.commit()
    db_session.refresh(trajeto)
    
    assert trajeto.idTrajeto is not None
    assert trajeto.comandosEnviados == "a1000da0001e"
    assert trajeto.comandosExecutados == "a1000da0001e"
    assert trajeto.status is True
    assert trajeto.tempo == 42

def test_trajeto_model_nullable_fields(db_session):
    """Testa registro de trajeto sem todos os campos preenchidos"""
    trajeto = TrajetoORM(
        comandosEnviados="a0050",
        tempo=5
    )
    
    db_session.add(trajeto)
    db_session.commit()
    db_session.refresh(trajeto)
    
    assert trajeto.comandosExecutados is None

def test_trajeto_model_incomplete_mission(db_session: Session):
    """Testa registrar trajeto interrompido"""
    trajeto = TrajetoORM(
        comandosEnviados="a1000da0500e",
        comandosExecutados="a1000d", # possivel interrupcao
        status=False,
        tempo=15,
    )
    
    db_session.add(trajeto)
    db_session.commit()
    db_session.refresh(trajeto)
    
    assert trajeto.status is False
    assert trajeto.comandosExecutados != trajeto.comandosEnviados