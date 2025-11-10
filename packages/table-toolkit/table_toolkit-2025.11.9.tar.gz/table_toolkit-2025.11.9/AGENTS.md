# Repository Guidelines

## Project Structure & Module Organization

- `src/tabkit/` is the installable package; configs, transforms, and helpers are under `data/`, `utils/`, and `config.py`.
- Re-exported APIs go through `src/tabkit/__init__.py`; update it when adding new public symbols.
- `tests/data/` holds `pytest` suites organised by feature; co-locate fixtures with the behaviors they cover.
- `examples/` contains developer-facing walkthroughs; refresh them when features change and keep wheel artefacts confined to `dist/`.

## Build, Test, and Development Commands

- Run `pixi install` to sync the dev environment defined by `pixi.lock` before hacking.
- `pixi run test` executes the `pytest` suite with the required OpenML env vars preset.
- `pixi run build` produces wheels and sdists via `python -m build`; inspect the output under `dist/`.
- For lightweight workflows, `pip install -e .[dev]` creates an editable install with the development extras.

## Coding Style & Naming Conventions

- Target Python 3.10+, follow PEP 8 with 4-space indents, and prefer explicit type hints.
- Classes stay `CamelCase`, functions and config keys use `snake_case`; keep module-level exports curated in `__all__`.
- Document complex flows with succinct docstrings like the existing ones and avoid impure logic at import time.

## Testing Guidelines

- Author new tests under `tests/` using `test_*.py` naming and descriptive `Test*` classes when grouping cases.
- Favour deterministic fixtures—small pandas DataFrames and numpy arrays—mirroring `tests/data/test_config.py`.
- Run `pixi run test` (or `OPENML_API_KEY=test OPENML_CACHE_DIR=/tmp/tabkit_pytest_cache pytest`) before pushing.

## Commit & Pull Request Guidelines

- Follow the repo history: short, present-tense, lower-case summaries (e.g., `rename split idx to fold idx`).
- Include context, breaking changes, and verification steps in the PR description; link issues when available.
- Ensure tests pass, docs/examples are updated, and note required env vars so reviewers can reproduce quickly.

## Environment & Configuration Tips

- `OPENML_API_KEY` and `OPENML_CACHE_DIR` must be exported before importing `tabkit.config`; use disposable values for tests.
- Optional `DATA_DIR` overrides the default `.data` cache root; choose a writable path in CI and local runs.
- Store secrets in local shells or `.env` files ignored by git, and prefer cached datasets when working offline.
