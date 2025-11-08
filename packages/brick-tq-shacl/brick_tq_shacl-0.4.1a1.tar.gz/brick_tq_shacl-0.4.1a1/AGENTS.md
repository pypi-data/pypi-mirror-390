# Repository Guidelines

## Project Structure & Module Organization
- `brick_tq_shacl/` contains the package; keep shared helpers in `__init__.py` and add engine glue next to related modules.
- Root `.ttl` files (e.g., `Brick.ttl`, `shapes.ttl`, `223p.ttl`) are canonical fixtures. Update only when upstream ontologies change and document the source.
- Utility scripts (`brick.py`, `s223.py`, `223.py`, `test.py`) double as integration smoke tests. Fold reusable logic back into the package.
- `dist/` stores build artifacts; regenerate with a build command rather than editing files in place.

## Build, Test, and Development Commands
- `uv sync` – create the managed virtualenv and install locked dependencies.
- `uv sync --extra withjre` – pull in the optional local JRE when contributors lack a system Java.
- `uv run python brick.py path/to/data.ttl` – validate a TTL graph against Brick + OntoEnv imports for regression checks.
- `uv run python s223.py` – reproduce the ASHRAE 223P validation workflow shipped with the repo.
- `uv build` – produce sdist/wheel via Hatchling; outputs land in `dist/`.

## Coding Style & Naming Conventions
- Follow PEP 8: 4-space indents, expressive names, module constants in `UPPER_SNAKE_CASE`.
- Prefer explicit imports from `rdflib`, `pytqshacl`, and `pathlib`; keep modules flat (`topquadrant_*.py`).
- Type-hint public functions and briefly note side effects (temporary files, owl:imports).

## Testing Guidelines
- No formal `pytest` suite yet; lean on the sample graphs plus `brick.py`/`s223.py` for smoke tests.
- Put new automated tests in `tests/` as `test_*.py` files; reuse small Turtle fixtures.
- Run `uv run python test.py` during review to print inferred triples and the validation report.

## Commit & Pull Request Guidelines
- Follow the existing Conventional Commit style (`type: message`), as seen in `git log` (`docs: ...`, `fix: ...`, `refactor: ...`).
- Reference related issues in the body, summarize graph/shape impacts, and note whether ontologies or generated artifacts changed.
- For pull requests, include: purpose, key commands executed, sample validation output, and any ontology sources or schema updates. Add screenshots only when the change affects human-readable reports.

## Environment & Dependency Tips
- Java 11+ must be on PATH; verify with `java -version` before inference.
- Missing Java? Install with `uv pip install ".[withjre]"` or `uv sync --extra withjre`; override via `BRICK_TQ_SHACL_JRE_HOME`, `BRICK_TQ_SHACL_JRE_VERSION`, or `BRICK_TQ_SHACL_JRE_VENDOR`.
- Use `uv lock` when constraints change; avoid editing `uv.lock`. For ad hoc installs, prefer `uv pip install --editable .`.
