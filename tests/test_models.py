import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import TrajetoORM
from app.database import Base

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Cria sessao do banco para cada teste"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_trajeto_model_creation(db_session):
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