import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite://"

@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# ── Helper functions ─────────────────────────────────────

def create_org(client, name="Test Company"):
    """Helper to create organization"""
    # Register admin first to create org
    res = client.post("/auth/register", json={
        "email": f"admin_{name}@test.com",
        "password": "admin123",
        "full_name": "Test Admin",
        "role": "admin",
        "organization_name": name
    })
    return res.json()

def get_token(client, email, password):
    """Helper to get JWT token"""
    res = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    return res.json().get("access_token")

def auth_header(token):
    """Helper to create auth header"""
    return {"Authorization": f"Bearer {token}"}