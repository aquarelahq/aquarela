import json
import sqlite3

from aquarela.db import database_url


def url(project, cid=""):
    return f"/api/projects/{project['id']}/classes" + (f"/{cid}" if cid else "")


def make(client, project, name, key=None):
    r = client.post(url(project), json={"name": name, "color": "#e86a92", "key": key})
    assert r.status_code == 201, r.text
    return r.json()


def test_crear_y_listar_en_orden_del_panel(client, project):
    a, b = make(client, project, "a", "1"), make(client, project, "b")
    assert (a["position"], b["position"]) == (0, 1)
    assert [c["name"] for c in client.get(url(project)).json()] == ["a", "b"]


def test_crear_valida_y_detecta_duplicados(client, project):
    make(client, project, "a", "1")
    bad = client.post(url(project), json={"name": "x", "color": "red"})
    assert bad.status_code == 422
    assert (
        client.post(
            url(project), json={"name": "x", "color": "#000000", "key": "0"}
        ).status_code
        == 422
    )
    dup_name = client.post(url(project), json={"name": "a", "color": "#000000"})
    assert (
        dup_name.status_code == 409 and dup_name.json()["error"]["code"] == "name_taken"
    )
    dup_key = client.post(
        url(project), json={"name": "z", "color": "#000000", "key": "1"}
    )
    assert dup_key.status_code == 409 and dup_key.json()["error"]["code"] == "key_taken"


def test_proyecto_inexistente_404(client):
    assert client.get("/api/projects/nope/classes").status_code == 404
    assert (
        client.post(
            "/api/projects/nope/classes", json={"name": "a", "color": "#000000"}
        ).status_code
        == 404
    )


def test_actualizar_campos(client, project):
    a = make(client, project, "a", "1")
    r = client.patch(
        url(project, a["id"]), json={"name": "b", "color": "#00ff00", "key": None}
    )
    assert r.status_code == 200
    assert r.json() | {"id": 0} == {
        "id": 0,
        "name": "b",
        "color": "#00ff00",
        "key": None,
        "position": 0,
    }
    assert client.patch(url(project, "nope"), json={"name": "x"}).status_code == 404
    assert client.patch(url(project, a["id"]), json={"name": None}).status_code == 422


def test_actualizar_posicion_reordena(client, project):
    _a, _b, c = (make(client, project, n) for n in "abc")
    r = client.patch(url(project, c["id"]), json={"position": 0})
    assert r.json()["position"] == 0
    listing = client.get(url(project)).json()
    assert [x["name"] for x in listing] == ["c", "a", "b"]
    assert [x["position"] for x in listing] == [0, 1, 2]


def test_actualizar_conflicto_409(client, project):
    make(client, project, "a", "1")
    b = make(client, project, "b")
    r = client.patch(url(project, b["id"]), json={"name": "a"})
    assert r.status_code == 409
    r = client.patch(url(project, b["id"]), json={"key": "1"})
    assert r.status_code == 409


def test_borrar_clase_libre(client, project):
    a = make(client, project, "a")
    assert client.delete(url(project, a["id"])).status_code == 204
    assert client.get(url(project)).json() == []
    assert client.delete(url(project, a["id"])).status_code == 404


def test_borrar_clase_en_uso_409(client, project, tmp_path):
    used, free = make(client, project, "used"), make(client, project, "free")
    con = sqlite3.connect(database_url().removeprefix("sqlite:///"))
    con.execute(
        "INSERT INTO images (id, project_id, rel_path, width, height, created_at, updated_at) "
        "VALUES ('i1', ?, 'a.png', 10, 10, 0, 0)",
        (project["id"],),
    )
    shapes = [{"id": "s1", "class_id": used["id"], "type": "point", "x": 1, "y": 2}]
    con.execute("INSERT INTO annotations VALUES ('i1', 1, ?, 0)", (json.dumps(shapes),))
    con.commit()
    con.close()

    r = client.delete(url(project, used["id"]))
    assert r.status_code == 409 and r.json()["error"]["code"] == "class_in_use"
    assert client.delete(url(project, free["id"])).status_code == 204
    assert [c["id"] for c in client.get(url(project)).json()] == [used["id"]]
