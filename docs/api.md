# API

Version 0.1. The core serves a JSON API under `/api`. All coordinates are in
image pixels. IDs are ULIDs, so they are unique, sortable and can be created
in the browser.

## Projects

```
GET    /api/projects                  List projects
POST   /api/projects                  Create a project from a folder  {name, path}
GET    /api/projects/{pid}            Project detail with image counts by status
PATCH  /api/projects/{pid}            Rename  {name}
DELETE /api/projects/{pid}            Delete the project (the images stay on disk)
```

## Classes

```
GET    /api/projects/{pid}/classes            List classes in panel order
POST   /api/projects/{pid}/classes            Create  {name, color, key}
PATCH  /api/projects/{pid}/classes/{cid}      Update  {name, color, key, position}
DELETE /api/projects/{pid}/classes/{cid}      Delete (409 if any label uses it)
```

## Images

```
GET    /api/projects/{pid}/images?status=todo&cursor=…&limit=100
                                      {items: [{id, name, width, height, status}], next}
GET    /api/images/{iid}/file         The original file
PATCH  /api/images/{iid}              Change status  {status}
```

`status` is one of `todo`, `in_progress`, `in_review`, `done`. Pages use a
cursor so they stay fast with 100,000 images. `next` is `null` on the last
page.

## Annotations

```
GET    /api/images/{iid}/annotations  {version, shapes}
PUT    /api/images/{iid}/annotations  Replace all shapes  {version, shapes}
```

`PUT` sends the `version` it last read. If someone saved in between, the
server answers `409` and the client reloads. On success the server returns the
new `version`.

A shape is a box, a polygon or a point, with `class_id` set to a class ID:

```json
{"id": "01JB…", "class_id": "01JA…", "type": "box", "x": 120, "y": 80, "w": 64, "h": 40}
{"id": "01JB…", "class_id": "01JA…", "type": "polygon", "points": [[10, 20], [40, 22], [30, 60]]}
{"id": "01JB…", "class_id": "01JA…", "type": "point", "x": 300, "y": 210}
```

In v0.2 live collaboration adds a WebSocket at `/api/images/{iid}/sync` that
carries Yjs updates. The rest of the API stays the same.

## Export

```
GET    /api/projects/{pid}/export?format=yolo|coco    Download a .zip
```

## Errors

Errors use the HTTP status code and this body:

```json
{"error": {"code": "version_conflict", "message": "The annotations changed since you loaded them."}}
```
