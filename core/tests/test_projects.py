def test_crear_y_listar(client, tmp_path):
    assert client.get("/api/projects").json() == []
    r = client.post("/api/projects", json={"name": " Cats ", "path": str(tmp_path)})
    assert r.status_code == 201
    created = r.json()
    assert created["name"] == "Cats" and len(created["id"]) == 26
    assert client.get("/api/projects").json() == [created]


def test_crear_valida_carpeta_y_nombre(client, tmp_path):
    r = client.post("/api/projects", json={"name": "x", "path": str(tmp_path / "nope")})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_path"
    r = client.post("/api/projects", json={"name": "  ", "path": str(tmp_path)})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_request"


def test_detalle_con_conteo_por_estado(client, project):
    r = client.get(f"/api/projects/{project['id']}")
    assert r.status_code == 200
    assert r.json()["image_counts"] == {
        "todo": 0,
        "in_progress": 0,
        "in_review": 0,
        "done": 0,
    }


def test_detalle_inexistente_404(client):
    r = client.get("/api/projects/nope")
    assert r.status_code == 404 and r.json()["error"]["code"] == "not_found"


def test_renombrar(client, project):
    r = client.patch(f"/api/projects/{project['id']}", json={"name": "Dogs"})
    assert r.status_code == 200 and r.json()["name"] == "Dogs"
    assert client.patch("/api/projects/nope", json={"name": "x"}).status_code == 404


def test_borrar_elimina_sus_clases_y_deja_la_carpeta(client, project, tmp_path):
    pid = project["id"]
    client.post(
        f"/api/projects/{pid}/classes", json={"name": "cat", "color": "#e86a92"}
    )
    assert client.delete(f"/api/projects/{pid}").status_code == 204
    assert client.get(f"/api/projects/{pid}").status_code == 404
    assert (tmp_path / "images").is_dir()
    assert client.delete(f"/api/projects/{pid}").status_code == 404
