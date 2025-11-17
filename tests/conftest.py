import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, AsyncMock
from app.main import app
from app.database import Base
from app.dependencies import get_db, get_mqtt_manager
from app.mqtt_manager import MQTTManager, MQTTClient

TEST_DATABASE_URL = "sqlite://"

@pytest.fixture
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mqtt_manager_mock():
    """Fornece uma instância de MQTTManager com client interno mocado."""
    mock_client_instance = MagicMock(spec=MQTTClient)
    mock_client_instance.connect = AsyncMock()
    mock_client_instance.disconnect = AsyncMock()
    mock_client_instance.publish = MagicMock()
    mock_client_instance.subscribe = MagicMock()
    
    manager_instance = MQTTManager(client_id="test_client")
    manager_instance.client = mock_client_instance
    return manager_instance

@pytest.fixture(name="client")
def client_fixture(db_session: Session, mqtt_manager_mock: MQTTManager):
    def get_db_override():
        return db_session

    def get_mqtt_override():
        return mqtt_manager_mock

    app.dependency_overrides[get_db] = get_db_override
    app.dependency_overrides[get_mqtt_manager] = get_mqtt_override

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()
