# Black Ops Architecture

## High-Level Layout

- `black_ops.py` is the guided launcher and main menu entry point.
- `black_ops_cli.py` is the interactive shell entry point.
- `core/` contains the service layer for config, policy, execution, telemetry, reporting, UI presentation, and compatibility fallbacks.
- `tools/` contains the operational modules grouped by domain.
- `data/` contains runtime data, configurations, rules, templates, and session state.
- `reports/` stores generated report output.
- `logs/` stores runtime logs and audit output.
- `tests/` contains unit, integration, functional, security, and performance coverage.

## Core Service Areas

- `core/runtime/` contains startup checks, dependency handling, and runtime helpers.
- `core/execution/` contains command execution, process running, tool dispatch, and command builders.
- `core/presentation/` contains launcher, menu, and shell output helpers.
- `core/reporting/` contains the system report writer and report helpers.
- `core/registry/` defines the visible tool catalog.
- `core/telemetry/` contains logging and run telemetry.
- `core/compat/` provides compatibility implementations when the full service stack is unavailable.
- `core/policy_engine.py` evaluates profiles, approvals, and execution constraints.
- `core/stats_service.py` persists usage counters in the session data area.

## Recent Cleanup

- Generated stats moved to `data/sessions/`.
- Generated reports moved to `reports/scans/`.
- The legacy `tools/scanner/` branch was consolidated into `tools/recon/`.
- Typos in directory names were corrected:
  - `perfomace_tests` to `performance_tests`
  - `disclamer` to `disclaimer`
  - `payloade_templates` to `payload_templates`

## Notes

- The repository still contains some historical directories such as `c2/`, `ai/`, and `web/` that may be active product areas or legacy support modules.
- If the project continues to grow, the next clean split would be grouping `core/` into subpackages such as runtime, policy, presentation, and compatibility.
