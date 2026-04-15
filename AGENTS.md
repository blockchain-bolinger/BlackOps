# Repository Guidelines

## Project Structure & Module Organization
The project is Python-first and centered on `black_ops.py` (main CLI/menu) and `black_ops_cli.py` (interactive shell). Core services live in `core/` (config, execution, ethics, logging, plugins). Operational modules are grouped under `tools/` by domain (`recon/`, `offensive/`, `stealth/`, `intelligence/`, `utils/`, `wireless/`, and `plugins/`). Web/API pieces are in `web/`, and AI helpers are in `ai/`.

Tests are under `tests/` with focused suites in `tests/unit_tests/`, `tests/integration_tests/`, `tests/functional_tests/`, `tests/security_tests/`, and performance folders.

## Build, Test, and Development Commands
- `python3 -m venv venv && source venv/bin/activate`: create and activate local virtualenv.
- `pip install -r requirements.txt`: install runtime + test deps.
- `./run.sh`: start via the project venv wrapper.
- `python3 black_ops.py --help`: inspect top-level CLI.
- `python3 black_ops_cli.py`: launch interactive shell.
- `pytest -q`: CI-aligned test command (`.github/workflows/tests.yml`).
- `python3 -m unittest discover -s tests/unit_tests -v`: run unit tests in the repository’s native `unittest` style.

## Coding Style & Naming Conventions
Use 4-space indentation and follow existing Python conventions:
- `snake_case` for functions, variables, and module names.
- `PascalCase` for classes.
- `UPPER_SNAKE_CASE` for constants.

Keep imports explicit and grouped (stdlib, third-party, local). New plugin implementations should follow `tools/plugins/<plugin_name>/plugin.py` and integrate with `PluginInterface` patterns already used in `tools/plugins/*`.

## Testing Guidelines
Write tests as `test_*.py` with `unittest.TestCase` classes and `test_*` methods. Prefer deterministic tests: isolate filesystem state with `tempfile`, clean env vars in `tearDown`, and avoid network-dependent behavior unless explicitly integration-scoped.

For changed core logic, add/extend tests in `tests/unit_tests/` first; use integration/functional suites only when behavior crosses module boundaries.

## Commit & Pull Request Guidelines
Current git history is sparse and uses short, direct summaries. Keep commits focused and imperative, for example: `core: enforce tool timeout handling`.

PRs should include:
- what changed and why,
- affected paths/modules,
- test commands run (for example, `pytest -q`),
- security impact notes when touching secrets/config/logging.

## Security & Configuration Tips
Do not commit real secrets. Treat `.env`, `secrets.json`, and sensitive values in `blackops_config.json` as local-only. Review outputs under `logs/` and `reports/` for accidental credential leakage before sharing artifacts.
