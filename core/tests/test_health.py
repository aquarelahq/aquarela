from fastapi.testclient import TestClient

from aquarela.app import app

client = TestClient(app)


def test_health_responde_ok():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.text == "ok"
