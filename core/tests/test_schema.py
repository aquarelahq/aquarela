import sqlite3

from fastapi.testclient import TestClient

from aquarela.app import app


def test_arranque_crea_todas_las_tablas_e_indices(tmp_path, monkeypatch):
    db = tmp_path / "fresh.db"
    monkeypatch.setenv("AQUARELA_DATABASE_URL", f"sqlite:///{db}")

    with TestClient(app):
        pass

    con = sqlite3.connect(db)
    names = {
        row[0]
        for row in con.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'index')"
        )
    }
    assert {"projects", "classes", "images", "annotations", "images_page"} <= names
