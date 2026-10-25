# Roadmap

Where Aquarela is going. Finished work moves to the [changelog](CHANGELOG.md).
The reasons behind each step are in the [design doc](DESIGN.md). Each item
links to its issue, and the issues of a version are grouped in a
[milestone](https://github.com/aquarelahq/aquarela/milestones).

## v0.1. Label alone, locally

- [x] Image canvas with pan, zoom and boxes
- [x] [API](docs/api.md) and [data model](docs/data-model.md)
- [x] Rust server skeleton and CI ([#3](https://github.com/aquarelahq/aquarela/issues/3))
- [ ] SQLite schema ([#4](https://github.com/aquarelahq/aquarela/issues/4))
- [ ] Projects and classes API ([#5](https://github.com/aquarelahq/aquarela/issues/5))
- [ ] Images API ([#6](https://github.com/aquarelahq/aquarela/issues/6))
- [ ] Annotations API ([#7](https://github.com/aquarelahq/aquarela/issues/7))
- [ ] Web app connected to the API ([#8](https://github.com/aquarelahq/aquarela/issues/8))
- [ ] Web app served from the binary ([#9](https://github.com/aquarelahq/aquarela/issues/9))
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
