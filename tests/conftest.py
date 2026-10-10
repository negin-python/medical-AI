import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from main import app
from database.connection import Base,get_database
from dependencies.auth import get_token

#read .env and add to  environment variebles
load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

test_engine = create_engine(TEST_DATABASE_URL)

testingsessionlocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit = False
)

ROLE_PERMISSION = {
    "admin":[
        "patient:read",
        "patient:create",
        "patient:update",
        "patient:delete"
    ],
    "doctor":[
        "patient:read",
        "patient:create",
        "patient:update"
    ],
    "nurse":["patient:read"]
}

def fake_get_token(role="admin"):
    return{
        "username":"test_user",
        "permissions":ROLE_PERMISSION[role]
    }

@pytest.fixture(scope="session",autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = testingsessionlocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(db):
    def override_get_database():
        yield db
    app.dependency_overrides[get_database]=override_get_database
    app.dependency_overrides[get_token] = fake_get_token

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_database,None)
    app.dependency_overrides.pop(get_token,None)

@pytest.fixture
def client_for_role(db):
    def create_client(role):
        def override_get_database():
            yield db
        def overrride_get_token():
            return fake_get_token(role)
        app.dependency_overrides[get_database] = override_get_database
        app.dependency_overrides[get_token] = overrride_get_token

        return TestClient(app)
    yield create_client

    app.dependency_overrides.pop(get_database,None)
    app.dependency_overrides.pop(get_token,None)
    