# Contributing

Thanks for your interest in Aquarela.

## Current status

Aquarela is in early development and is **not open to code contributions
yet**. You are welcome to:

- Report a bug.
- Propose an idea or a feature.
- Ask a question.

Open an [issue](https://github.com/aquarelahq/aquarela/issues) for any of
these. The maintainer reviews every proposal and decides whether it fits the
[roadmap](ROADMAP.md). Pull requests are only merged after the maintainer
approves them, and pull requests without an approved issue may be closed.

This document is also the workflow the maintainer follows, so it stays valid
when the project opens up.

## Where things are

| File | What it holds |
|---|---|
| [DESIGN.md](DESIGN.md) | What Aquarela is and why it is built this way |
| [docs/api.md](docs/api.md) | The HTTP API |
| [docs/data-model.md](docs/data-model.md) | The database schema |
| [ROADMAP.md](ROADMAP.md) | What comes next |
| [CHANGELOG.md](CHANGELOG.md) | What changed in each version |

## Workflow

Every change, including the maintainer's, follows these steps.

1. **Issue first.** Describe the change in an issue and wait until it is
   approved. Small fixes such as typos can skip this.
2. **Design before code.** If the change touches the API or the data model,
   update `docs/api.md` or `docs/data-model.md` first, in the same pull
   request. Big decisions go in `DESIGN.md`.
3. **Branch from `main`.** Name it after what it does:
   - `feat/polygon-tool`
   - `fix/zoom-on-safari`
   - `docs/export-formats`
4. **Commit.** Write each message as one short sentence in English, in the
   imperative, with no prefix. For example, `Add polygon tool` or
   `Fix zoom jumping on Safari`.
5. **Update the records.**
   - Add a line under `[Unreleased]` in `CHANGELOG.md`.
   - Tick the box in `ROADMAP.md` if the change finishes an item.
6. **Open a pull request** to `main`, linked to its issue. Keep it small: one
   change per pull request.
7. **Checks and review.** CI must pass, and the maintainer reviews and merges
   with squash, so each pull request becomes one commit on `main`.

`main` must always build and run.

## Development

### Web app

```bash
cd web
npm install
npm run dev      # http://localhost:5173
npm run build    # type check and production build, the same check CI runs
```

### Core (Rust)

Not started yet. When it is, it will build with `cargo build` and must pass
`cargo fmt --check`, `cargo clippy` and `cargo test`.

## Code style

- **TypeScript.** Strict mode, function components, and no `any`.
- **Rust.** Format with `rustfmt` and fix every `clippy` warning.
- **Comments.** Short, and only where the code does not explain itself.
- **Coordinates.** Labels are always stored in image pixels, never screen
  pixels.

## Releases

Only the maintainer releases.

1. Move the `[Unreleased]` items in `CHANGELOG.md` to a new version with
   today's date.
2. Bump the version in `python/pyproject.toml`, `npm/package.json` and
   `rust/Cargo.toml`.
3. Commit with the message `Release X.Y.Z`, then tag and push:

   ```bash
   git tag vX.Y.Z && git push origin main --tags
   ```

   The release workflow publishes to PyPI, npm and crates.io.

Versions follow [Semantic Versioning](https://semver.org). Until 1.0, a new
minor version (0.2, 0.3, and so on) may break things.

## License

By contributing you agree that your work is released under the
[MIT license](LICENSE).
