import pytest
from fastapi.testclient import TestClient

from aquarela.app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AQUARELA_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    with TestClient(app) as c:
        yield c


@pytest.fixture
def project(client, tmp_path):
    folder = tmp_path / "images"
    folder.mkdir()
    r = client.post("/api/projects", json={"name": "Cats", "path": str(folder)})
    assert r.status_code == 201
    return r.json()
