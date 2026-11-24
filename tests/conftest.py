import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Character
from app.scripts.populate_db import characters_data

# A throwaway database that lives in memory (RAM) and disappears when the tests finish.
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    """A fake browser that sends requests straight to the app, using the test database."""
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_db():
    """Runs before EVERY test: start each one with empty tables."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture
def seeded_db():
    """Fill the test database with the same 12 characters the real one starts with."""
    with TestingSessionLocal() as db:
        db.add_all(Character(**character) for character in characters_data)
        db.commit()
    return characters_data


# SAMPLE CHARACTER
@pytest.fixture
def sample_character():
    return {
        "name": "Ralph Cifaretto",
        "actor": "Joe Pantoliano",
        "role": "Capo",
        "status": "Dead",
        "first_season": 3,
        "last_season": 4,
    }


# UPDATED CHARACTER
@pytest.fixture
def updated_character():
    return {
        "name": "Richie Aprile",
        "actor": "David Proval",
        "role": "Soldier",
        "status": "Dead",
        "first_season": 2,
        "last_season": 2,
    }


# CREATED CHARACTER
@pytest.fixture
def created_character(client, sample_character):
    response = client.post("/characters/", json=sample_character)

    assert response.status_code == 201

    return response.json()
