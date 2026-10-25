from fastapi.testclient import TestClient

from aquarela.app import app

client = TestClient(app)


def test_health_responde_ok():
    # TestClient manda la request a la app sin abrir un puerto
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.text == "ok"
