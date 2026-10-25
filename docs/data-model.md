# Data model

Version 0.1, stored in SQLite. The schema also runs on Postgres: IDs are text
(ULIDs), times are integers (Unix milliseconds) and JSON is text (JSONB on
Postgres).

```sql
CREATE TABLE projects (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  root_path   TEXT NOT NULL,              -- folder that holds the images
  created_at  INTEGER NOT NULL,
  updated_at  INTEGER NOT NULL
);

CREATE TABLE classes (
  id          TEXT PRIMARY KEY,
  project_id  TEXT NOT NULL REFERENCES projects ON DELETE CASCADE,
  name        TEXT NOT NULL,
  color       TEXT NOT NULL,              -- '#e86a92'
  hotkey      TEXT,                       -- '1' to '9'
  position    INTEGER NOT NULL,           -- order in the panel
  UNIQUE (project_id, name),
  UNIQUE (project_id, hotkey)
);

CREATE TABLE images (
  id          TEXT PRIMARY KEY,
  project_id  TEXT NOT NULL REFERENCES projects ON DELETE CASCADE,
  rel_path    TEXT NOT NULL,              -- relative to root_path
  width       INTEGER NOT NULL,
  height      INTEGER NOT NULL,
  status      TEXT NOT NULL DEFAULT 'todo'
              CHECK (status IN ('todo', 'in_progress', 'in_review', 'done')),
  created_at  INTEGER NOT NULL,
  updated_at  INTEGER NOT NULL,
  UNIQUE (project_id, rel_path)
);

CREATE INDEX images_page ON images (project_id, status, id);

CREATE TABLE annotations (
  image_id    TEXT PRIMARY KEY REFERENCES images ON DELETE CASCADE,
  version     INTEGER NOT NULL,           -- goes up on every save
  shapes      TEXT NOT NULL,              -- JSON array of shapes (see api.md)
  updated_at  INTEGER NOT NULL
);
```

## Decisions

- **One JSON document of shapes per image**, not one row per shape. It matches
  the `PUT` in the API, and in v0.2 each image's Yjs document becomes the
  source of truth, so a shapes table would only be a copy to keep in sync.
- **Images are never copied.** Only their path inside the project folder is
  stored.
- **A class in use cannot be deleted** (the API answers `409`), so labels are
  never lost by accident.
- **`images_page`** lets the image list page by cursor and filter by status
  without scanning the whole table.

## Added in v0.2

```
users        (id, name, email, password_hash, created_at)
members      (project_id, user_id, role)        -- owner, labeler, reviewer
reviews      (id, image_id, reviewer_id, decision, comment, created_at)
images       + assignee_id
annotations  + ydoc BLOB                        -- Yjs document state
```
