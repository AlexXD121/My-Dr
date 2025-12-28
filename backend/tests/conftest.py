import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db, Base
from models import User, Conversation, Message, MedicalRecord

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        firebase_uid="test_uid_123",
        email="test@example.com",
        display_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_conversation(db_session, sample_user):
    """Create a sample conversation for testing."""
    conversation = Conversation(
        user_id=sample_user.id,
        title="Test Conversation",
        consultation_type="general"
    )
    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)
    return conversation

@pytest.fixture
def sample_message(db_session, sample_conversation):
    """Create a sample message for testing."""
    message = Message(
        conversation_id=sample_conversation.id,
        content="Test message content",
        sender="user"
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    return message

@pytest.fixture
def sample_medical_record(db_session, sample_user):
    """Create a sample medical record for testing."""
    record = MedicalRecord(
        user_id=sample_user.id,
        record_type="visit",
        title="Annual Checkup",
        description="Routine annual physical examination",
        date_recorded="2024-01-15",
        healthcare_provider="Dr. Smith"
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record