# Repository Guidelines

## Project Structure & Module Organization
- `black_ops.py` is the main entry point; `black_ops_cli.py` provides CLI glue.
- Core framework logic lives in `core/`, supporting utilities in `utils/`, and tool implementations in `tools/`.
- Operational modules include `c2/` (command & control), `web/`, `ai/`, and `payloads/`.
- Data and outputs are organized under `data/`, `logs/`, `reports/`, `backups/`, and `tmp/`.
- Tests are under `tests/` with suites in `unit_tests/`, `functional_tests/`, `integrations_tests/`, `secruity_tests/`, and `perfomace_tests/` (directory names are misspelled in-repo; keep them as-is).

## Build, Test, and Development Commands
- `./install.sh`: installs system dependencies, sets up `venv/`, and installs Python packages.
- `./run.sh`: activates `venv/` and runs `python3 black_ops.py`.
- `python3 black_ops.py --help`: shows CLI usage (preferred for exploring commands).
- `python -m unittest discover -s tests`: runs the full test suite using `unittest` discovery.

## Coding Style & Naming Conventions
- Follow standard Python conventions: 4-space indentation, `snake_case` for functions/variables, and `PascalCase` for classes.
- Keep modules cohesive and place shared logic in `core/` or `utils/` rather than duplicating.
- `install.sh` installs `pylint` and `autopep8`; use them to lint/format if you add non-trivial code.

## Testing Guidelines
- Tests are `unittest`-based and named `test_*.py` (e.g., `tests/test_core.py`).
- Prefer adding tests next to the relevant suite folder (unit, functional, integration, security, performance).
- If you use `pytest`, it should still discover `unittest` tests without changes, but there is no repo-specific pytest config.

## Commit & Pull Request Guidelines
- This repo does not include Git history in the workspace, so no commit message convention is implied.
- For PRs, include a clear summary, the area touched (e.g., `core/` or `tools/`), and test evidence (command + result). Add screenshots only if UI changes are involved.

## Security & Configuration Tips
- Use this framework only for authorized security testing per the README disclaimer.
- Treat `secrets.json` and `blackops_config.json` as sensitive; avoid committing real credentials or target data.
- Keep generated artifacts in `logs/` and `reports/` out of version control unless explicitly required.
