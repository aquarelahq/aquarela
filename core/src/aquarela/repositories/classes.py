import json

from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError

from aquarela.errors import ApiError
from aquarela.utils import new_id

# API field -> column of the `classes` table.
COLUMNS = {"name": "name", "color": "color", "key": "hotkey"}


def _view(row) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "color": row.color,
        "key": row.hotkey,
        "position": row.position,
    }


def _conflict(exc: IntegrityError) -> ApiError:
    if "hotkey" in str(exc.orig):
        return ApiError(409, "key_taken", "Another class already uses that key.")
    return ApiError(409, "name_taken", "Another class already has that name.")


class ClassRepository:
    """All access to the `classes` table of one project."""

    def __init__(self, conn: Connection, project_id: str) -> None:
        self.conn = conn
        self.project_id = project_id

    def _ordered_ids(self) -> list[str]:
        rows = self.conn.execute(
            text("SELECT id FROM classes WHERE project_id = :p ORDER BY position, id"),
            {"p": self.project_id},
        )
        return [r.id for r in rows]

    def list(self) -> list[dict]:
        rows = self.conn.execute(
            text("SELECT * FROM classes WHERE project_id = :p ORDER BY position, id"),
            {"p": self.project_id},
        )
        return [_view(r) for r in rows]

    def get(self, cid: str) -> dict:
        row = self.conn.execute(
            text("SELECT * FROM classes WHERE id = :id AND project_id = :p"),
            {"id": cid, "p": self.project_id},
        ).one_or_none()
        if row is None:
            raise ApiError(404, "not_found", "Class not found.")
        return _view(row)

    def create(self, name: str, color: str, key: str | None) -> dict:
        cid = new_id()
        try:
            self.conn.execute(
                text(
                    "INSERT INTO classes (id, project_id, name, color, hotkey, position) "
                    "VALUES (:id, :p, :name, :color, :key, (SELECT "
                    "COALESCE(MAX(position) + 1, 0) FROM classes WHERE project_id = :p))"
                ),
                {
                    "id": cid,
                    "p": self.project_id,
                    "name": name,
                    "color": color,
                    "key": key,
                },
            )
        except IntegrityError as exc:
            raise _conflict(exc) from exc
        return self.get(cid)

    def update(self, cid: str, changes: dict, position: int | None = None) -> dict:
        """Apply `changes` (API field names) and optionally move to `position`."""
        self.get(cid)
        try:
            for field, value in changes.items():
                self.conn.execute(
                    text(f"UPDATE classes SET {COLUMNS[field]} = :v WHERE id = :id"),
                    {"v": value, "id": cid},
                )
            if position is not None:
                self._move(cid, position)
        except IntegrityError as exc:
            raise _conflict(exc) from exc
        return self.get(cid)

    def _move(self, cid: str, position: int) -> None:
        ids = [i for i in self._ordered_ids() if i != cid]
        ids.insert(min(position, len(ids)), cid)
        for index, other in enumerate(ids):
            self.conn.execute(
                text("UPDATE classes SET position = :i WHERE id = :id"),
                {"i": index, "id": other},
            )

    def is_used(self, cid: str) -> bool:
        # Shapes are one JSON document per image. The LIKE narrows the scan to
        # candidates (ULIDs are unique); parsing confirms the match.
        rows = self.conn.execute(
            text(
                "SELECT a.shapes FROM annotations a JOIN images i ON i.id = a.image_id "
                "WHERE i.project_id = :p AND a.shapes LIKE :pat"
            ),
            {"p": self.project_id, "pat": f"%{cid}%"},
        )
        return any(
            s.get("class_id") == cid for (shapes,) in rows for s in json.loads(shapes)
        )

    def delete(self, cid: str) -> None:
        self.get(cid)
        if self.is_used(cid):
            raise ApiError(409, "class_in_use", "Some labels use this class.")
        self.conn.execute(text("DELETE FROM classes WHERE id = :id"), {"id": cid})
