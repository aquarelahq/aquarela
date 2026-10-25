# Roadmap

Where Aquarela is going. Finished work moves to the [changelog](CHANGELOG.md).
The reasons behind each step are in the [design doc](DESIGN.md).

## v0.1. Label alone, locally

- [x] Image canvas with pan, zoom and boxes
- [x] [API](docs/api.md) and [data model](docs/data-model.md)
- [ ] Rust core with axum and SQLite
- [ ] Open a local folder of images
- [ ] Save classes and labels
- [ ] Polygons and points
- [ ] Export to YOLO and COCO
- [ ] Docker image and single binary

## v0.2. Label together

- [ ] Live sync with Yjs over WebSocket
- [ ] Users, login and roles (owner, labeler, reviewer)
- [ ] Review flow (accept or request changes)
- [ ] Postgres for teams

## Later

- [ ] AI-assisted labeling with models running as separate services
- [ ] Large images loaded as tiles
- [ ] Pascal VOC export
