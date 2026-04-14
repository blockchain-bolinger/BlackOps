# Black Ops Framework v3.0

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)
![Version](https://img.shields.io/badge/Version-3.0-orange)

Black Ops is a modular cybersecurity framework for authorized security testing, OSINT workflows, reporting, and plugin-based operations.

## Important Notice

This framework may only be used in authorized environments.

Allowed:
- Your own systems and lab environments
- CTF and training scenarios
- Authorized penetration tests

Not allowed:
- Unauthorized attacks
- Abuse against third-party systems
- Any illegal use

## Getting Started

Two entry points are available:

```bash
python3 black_ops.py
python3 black_ops_cli.py
```

The detailed usage guide is available in [USAGE.md](USAGE.md).
For a faster introduction, see [NEW_USERS.md](NEW_USERS.md).
The architecture overview is available in [docs/architecture.md](docs/architecture.md).

## Overview

- `black_ops.py` starts the guided main application with menu, checks, and reporting
- `black_ops_cli.py` provides the interactive shell for faster, repeatable workflows
- `core/` contains configuration, execution, policy, telemetry, reporting, and UI helpers
- `tools/` contains the domain modules for recon, OSINT, utility, and test workflows
- `tests/` contains unit, integration, and functional suites

## Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m pytest -q
```

## Project Structure

- `black_ops.py` - main menu and launcher
- `black_ops_cli.py` - interactive shell
- `core/` - services, policies, telemetry, and reporting
- `tools/` - module library
- `tests/` - tests
- `web/` - web and dashboard components

## License

MIT
