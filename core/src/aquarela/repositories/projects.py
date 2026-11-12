from sqlalchemy import Connection, text

from aquarela.errors import ApiError
from aquarela.utils import new_id, now_ms

STATUSES = ("todo", "in_progress", "in_review", "done")


def _view(row) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "path": row.root_path,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


class ProjectRepository:
    """All access to the `projects` table."""

    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def list(self) -> list[dict]:
        rows = self.conn.execute(text("SELECT * FROM projects ORDER BY id"))
        return [_view(r) for r in rows]

    def get(self, pid: str) -> dict:
        row = self.conn.execute(
            text("SELECT * FROM projects WHERE id = :id"), {"id": pid}
        ).one_or_none()
        if row is None:
            raise ApiError(404, "not_found", "Project not found.")
        return _view(row)

    def create(self, name: str, root_path: str) -> dict:
        pid = new_id()
        now = now_ms()
        self.conn.execute(
            text(
                "INSERT INTO projects (id, name, root_path, created_at, updated_at) "
                "VALUES (:id, :name, :path, :now, :now)"
            ),
            {"id": pid, "name": name, "path": root_path, "now": now},
        )
        return self.get(pid)

    def rename(self, pid: str, name: str) -> dict:
        self.get(pid)
        self.conn.execute(
            text("UPDATE projects SET name = :name, updated_at = :now WHERE id = :id"),
            {"name": name, "now": now_ms(), "id": pid},
        )
        return self.get(pid)

    def image_counts(self, pid: str) -> dict[str, int]:
        counts = dict.fromkeys(STATUSES, 0)
        rows = self.conn.execute(
            text(
                "SELECT status, COUNT(*) AS n FROM images "
                "WHERE project_id = :p GROUP BY status"
            ),
            {"p": pid},
        )
        for row in rows:
            counts[row.status] = row.n
        return counts

    def delete(self, pid: str) -> None:
        self.get(pid)
        self.conn.execute(text("DELETE FROM projects WHERE id = :id"), {"id": pid})
