# Aquarela design

Status: draft, October 2026.

## Problem

Teams that train vision models need to label thousands of images. Today they
usually pick one of three trade-offs. They upload their images to a hosted
service and accept that their data lives in someone else's cloud. They self-host
a tool whose team features (roles, review) sit behind a paid tier. Or they use a
desktop app that works well for one person but has no way to share work.

Aquarela removes the trade-off. It is a labeling tool that runs on your own
machine or server, lets a whole team label together, and has no paid tier.
Everything is MIT licensed.

## Goals

- Label images with boxes, polygons and points, fast, mostly from the keyboard.
- Run anywhere with one command, with no account and no internet connection.
- Keep every image and label on infrastructure the user controls.
- Let several people label the same project at the same time, including offline,
  and merge their work without conflicts.
- Export to the formats people train with (YOLO, COCO, Pascal VOC).

## Non-goals for now

- AI-assisted labeling. It comes later (see Later), once the labeling and
  collaboration core is solid.
- Video, point clouds, audio and text labeling. Images first.
- Training models inside Aquarela. It labels data; training happens elsewhere.
- A hosted cloud offering.
- Workforce management (payments, worker marketplaces).

## Users

- A researcher labeling field images alone on a laptop, sometimes with no
  connection.
- A small team (2 to 20 people) in a lab or startup sharing one server, with
  labelers and reviewers.

## How it feels

1. Run one command and open `localhost:8080`.
2. Create a project, drop a folder of images, define classes.
3. Label with the keyboard. `B` draws a box, `P` a polygon, `K` a point, `1` to
   `9` pick the class.
4. Invite a teammate. You see their cursor and their labels appear live.
5. A reviewer accepts or sends back each image.
6. Export the dataset and train.

## Architecture

Aquarela has two parts.

### Core (Rust)

One program that holds everything. It ships as a Docker image and as a single
binary.

- **HTTP and WebSocket server** with axum. Serves the API, the live sync channel
  and the web app itself (embedded in the binary).
- **Storage.** SQLite by default, Postgres for teams. Images live on disk or in
  any S3 compatible bucket the user points to. Images are never copied anywhere
  else.
- **Sync.** Each image's annotations are a Yjs document, handled on the server
  by `yrs`, the official Rust port. Clients send small updates, the server
  merges and persists them, and broadcasts them to everyone on that image.
- **Export.** YOLO, COCO and Pascal VOC writers.

### Web app (TypeScript)

- React with Vite. The canvas is drawn with Konva, which handles thousands of
  shapes per image.
- Labels are edited in a local Yjs document stored in IndexedDB, so the app
  keeps working offline and syncs when the connection returns.
- Shared logic (geometry, format conversion) is written once in Rust and
  compiled to WebAssembly so the browser and the server behave the same.

### Canvas

The workspace is an endless canvas, and the image is a sheet lying on it, the
way a watercolor sits on a table. You move around the canvas and paint labels
on the sheet.

- The canvas holds one image at a time. `←` and `→` move to the previous or
  next image. A small bar fixed at the bottom edge of the canvas shows only the
  position (`5 / 128`) with previous and next buttons. It does not move with
  the image. The image name and status live in the side panel, above the
  classes.
- Scroll or Space + drag moves the canvas. Pinch or Ctrl + scroll zooms toward
  the cursor. `F` fits the image to the screen.
- Coordinates live in image pixels, never screen pixels, so labels stay exact
  at any zoom.
- Nothing is drawn on top of the image except labels and teammates' cursors.
  Tools, classes and status live in the panels around the canvas.
- Large images (drone and satellite photos) are loaded as tiles at the zoom
  level being viewed, so a 20,000 pixel image opens instantly.

How it is built:

- A single `Canvas` component, made for still images only. There is no video
  canvas and no frame logic.
- One camera (pan x, pan y, zoom) applied to a single Konva group. The image
  sits at (0, 0) in that group and every shape is stored and drawn in image
  pixels, so no shape ever needs offset or scale math of its own.
- Zoom is exponential and centered on the cursor, between 10% and 800%.
  Panning moves exactly as far as the mouse moves.
- Strokes, handles and labels are drawn at `1 / zoom`, so they keep the same
  size on screen at any zoom.
- Layers, bottom to top: image, shapes, the shape being drawn and selection
  handles, teammates' cursors. Each is its own small component.
- Tools are small state machines (idle, drawing, editing) that receive pointer
  events in image pixels, so adding a new tool never touches the canvas code.

## Data model

- **Project**: name, classes (name, color, hotkey), members and their roles.
- **Image**: file location, size, status (`todo`, `in_progress`, `in_review`,
  `done`), assignee.
- **Annotation document**: one Yjs document per image holding its shapes. Each
  shape has an id, type (`box`, `polygon`, `point`), class, coordinates and
  author.
- **Review**: image, reviewer, decision (`accepted`, `changes_requested`),
  comment.

Roles are `owner`, `labeler` and `reviewer`. All of them are free.

## Install

With Docker:

```bash
docker run -p 8080:8080 -v ~/aquarela-data:/data ghcr.io/aquarelahq/aquarela
```

Without Docker, download the binary for your system and run `aquarela`.

Larger teams use the Docker Compose file in `deploy/`, which adds Postgres and
an optional S3 bucket.

## Security

- Nothing leaves the machine. Aquarela makes no outbound calls and has no
  telemetry.
- Team mode requires login. Passwords are hashed with Argon2, and OIDC sign-in
  is supported for organizations that have it.

## MVP (v0.1)

The first release is deliberately small and complete.

- One user, local, no login.
- Image projects from a local folder.
- Boxes, polygons and points, with classes and hotkeys.
- Export to YOLO and COCO.
- Docker image and single binary.

The sync layer is designed in from day one so collaboration in v0.2 does not
require a rewrite.

## Plan

- Weeks 1 to 2. Rust core skeleton, project and image API, SQLite, web app
  showing images and drawing boxes.
- Weeks 3 to 4. Polygons, points, classes, hotkeys, export.
- Week 5. Docker image, binaries, docs, demo video. Release v0.1 and share it.
- Weeks 6 to 10. Yjs sync, users and roles, review flow. Release v0.2.

## Later

AI-assisted labeling. Models (YOLO, SAM, or your own) run as separate services
and speak a small HTTP contract (`GET /info`, `POST /predict` returning shapes).
Aquarela can start them as containers or register them by URL. This is designed
after v0.2, on top of the collaboration core.

## Repository layout

```
core/        Rust workspace (server, sync, storage, export)
web/         TypeScript web app
deploy/      Dockerfile, Compose files
docs/        Documentation
```

## Open questions

- Large datasets: how to page and cache 100,000 images in the browser.
- Whether to support labeling straight from S3 without a local copy in v0.1.
