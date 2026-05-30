import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.models import Usuario
from app.auth.auth import hash_password, create_access_token

SQLITE_URL = "sqlite:///./test.db"

engine_test = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def db():
    app.dependency_overrides[get_db] = override_get_db
    db = SessionTest()
    yield db
    db.rollback()
    db.close()
    app.dependency_overrides.clear()


@pytest.fixture()
def client(db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def usuario_de_prueba(db):
    usuario = Usuario(
        nombre="Usuario Prueba",
        email="prueba@test.com",
        hashed_password=hash_password("Password123"),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    yield usuario
    db.delete(usuario)
    db.commit()


@pytest.fixture()
def token_de_prueba(usuario_de_prueba):
    return create_access_token(data={"sub": str(usuario_de_prueba.id)})


@pytest.fixture()
def headers_auth(token_de_prueba):
    return {"Authorization": f"Bearer {token_de_prueba}"}
