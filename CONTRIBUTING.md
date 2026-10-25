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
4. **Commit** following
   [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
   Write `type(scope): description` in English, in the imperative and in
   lowercase:

   ```
   feat(web): add polygon tool
   fix(web): stop zoom jumping on Safari
   docs: describe export formats
   ```

   | Type | Use it for |
   |---|---|
   | `feat` | A new feature |
   | `fix` | A bug fix |
   | `docs` | Documentation only |
   | `refactor` | Code changes that neither fix a bug nor add a feature |
   | `perf` | Performance |
   | `test` | Tests |
   | `build` | Dependencies and build setup |
   | `ci` | GitHub Actions |
   | `chore` | Anything else, such as releases |

   The scope is optional and names the part touched: `web`, `core` or
   `deploy`. A breaking change adds `!` after the type, as in
   `feat(core)!: rename the shapes field`, and explains it in the body under
   `BREAKING CHANGE:`.
5. **Update the records.**
   - Add a line under `[Unreleased]` in `CHANGELOG.md`.
   - Tick the box in `ROADMAP.md` if the change finishes an item.
6. **Open a pull request** to `main`, linked to its issue. Keep it small: one
   change per pull request. Its title follows the same commit format, because
   it becomes the commit message on `main`.
7. **Checks and review.** CI must pass, and the maintainer reviews and merges
   with squash, so each pull request becomes one commit on `main`.

`main` must always build and run.

## Pull request size

A pull request does one thing. If its title needs an "and", it is probably
two pull requests.

Aim for fewer than 200 changed lines. The limit is 400. Reviews lose quality
beyond that size, so bigger changes are split into a series of smaller pull
requests that each build and pass CI on their own. Lockfiles, generated files
and snapshots do not count toward the limit.

CI fails when a pull request goes over 400 lines. Only the maintainer can
allow an exception, by adding the `size/exception` label.

## AI tools

You may use any AI tool to write code, docs or tests. You are responsible for
every line you submit, the same as if you had typed it yourself. That means
you understand the whole change, can explain any part of it in review, and
have run and tested it.

Declare AI usage in the pull request template. Trivial help such as
autocomplete, formatting or renaming does not need to be declared.

Make sure the output does not copy code from others under a license that is
not compatible with MIT, and that the terms of the tool allow you to
contribute what it produced.

The maintainer may ask you to explain any part of a pull request, and may
close it without review if you cannot. Pull requests that were clearly not
reviewed by a person are closed.

This policy follows the
[Linux Foundation guidance on generative AI](https://www.linuxfoundation.org/legal/generative-ai)
and the Linux kernel guides on
[tool-generated content](https://docs.kernel.org/process/generated-content.html)
and [AI coding assistants](https://docs.kernel.org/process/coding-assistants.html).

## Development

### Web app

```bash
cd web
npm install
npm run dev      # http://localhost:5173
npm run build    # type check and production build, the same check CI runs
```

### Core (Python)

```bash
cd core
uv run aquarela  # http://127.0.0.1:8080/api/health
uv run pytest
```

Before opening a pull request, run the same checks as CI:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

## Code style

- **TypeScript.** Strict mode, function components, and no `any`.
- **Python.** Format and lint with `ruff`, and type hints on every function.
- **Comments.** Short, and only where the code does not explain itself.
- **Coordinates.** Labels are always stored in image pixels, never screen
  pixels.

## Releases

Only the maintainer releases.

1. Move the `[Unreleased]` items in `CHANGELOG.md` to a new version with
   today's date.
2. Bump the version in `core/pyproject.toml`, `npm/package.json` and
   `rust/Cargo.toml`.
3. Commit with the message `chore: release X.Y.Z`, then tag and push:

   ```bash
   git tag vX.Y.Z && git push origin main --tags
   ```

   The release workflow publishes to PyPI, npm and crates.io.

Versions follow [Semantic Versioning](https://semver.org). Until 1.0, a new
minor version (0.2, 0.3, and so on) may break things.

## License

By contributing you agree that your work is released under the
[MIT license](LICENSE).
