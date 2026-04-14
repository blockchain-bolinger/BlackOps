#!/usr/bin/env python3
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, request, Response
import os
from pathlib import Path
import uuid

from core.config_manager import ConfigManager
from core.blackops_logger import BlackOpsLogger
from core.evidence_store import EvidenceStore
from core.execution_service import ExecutionService
from core.metrics import MetricsCollector
from core.policy_engine import PolicyEngine
from core.telemetry import ExecutionTelemetry
from core.process_runner import SafeProcessRunner, ProcessRunnerError
from core.redaction_utils import redact_data, redact_text
from core.tool_contract import ToolResult

app = Flask(__name__)
app_start = datetime.now(timezone.utc)
config_manager = ConfigManager()
metrics_collector = MetricsCollector()
logger = BlackOpsLogger("blackops_web")
policy_engine = PolicyEngine(config_manager.config)
telemetry = ExecutionTelemetry()
evidence_store = EvidenceStore()
base_dir = Path.cwd().resolve()
tools_dir = (base_dir / "tools").resolve()
process_runner = SafeProcessRunner(allowed_roots=[base_dir, tools_dir])


def _build_execution_service():
    return ExecutionService(
        process_runner=process_runner,
        base_dir=base_dir,
        tools_dir=tools_dir,
        policy_engine=policy_engine,
        telemetry=telemetry,
        profile_name=config_manager.get("policy.default_profile", "lab"),
    )

# In-Memory "Datenbank" für Sessions
sessions = []

@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/v1/overview')
def overview():
    return jsonify(
        {
            "telemetry": telemetry.snapshot(),
            "evidence": evidence_store.stats(),
            "evidence_records": evidence_store.recent(limit=10),
            "profiles": policy_engine.available_profiles(),
            "active_profile": config_manager.get("policy.default_profile", "lab"),
        }
    )

@app.route('/api/v1/tools')
def list_tools():
    tools = []
    for root, dirs, files in os.walk("tools"):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                tools.append(os.path.join(root, file))
    return jsonify(tools)

@app.route('/api/v1/run', methods=['POST'])
def run_tool():
    data = request.json or {}
    tool_path = data.get('tool')
    args = data.get('args', [])
    profile = data.get("profile") or config_manager.get("policy.default_profile", "lab")
    approved = bool(data.get("approved", False))
    action = data.get("action", "web_execution")
    target = data.get("target")
    module_category = data.get("module_category")
    correlation_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.set_correlation_id(correlation_id)

    try:
        timeout = config_manager.get("runtime.task_timeout_seconds", 30)
        service = _build_execution_service()
        logger.audit("web", "run_tool", str(tool_path), status="REQUESTED")
        result = service.execute_tool(
            tool_path,
            args=args,
            timeout=timeout,
            cwd=base_dir,
            capture_output=True,
            profile_name=profile,
            approved=approved,
            action=action,
            target=target,
            module_category=module_category,
            correlation_id=correlation_id,
        )
        payload = result.to_dict()
        payload["errors"] = [redact_text(str(item)) for item in payload.get("errors", [])]
        if isinstance(payload.get("data"), dict):
            payload["data"] = redact_data(payload["data"])
        if config_manager.get("policy.telemetry_enabled", True) and isinstance(result.data, dict):
            evidence_store.ingest_result(
                source_tool=str(tool_path),
                profile=profile,
                correlation_id=correlation_id,
                run_id=payload["meta"].get("run_id", correlation_id),
                result=payload,
                target=str(target or tool_path or ""),
                metadata={
                    "module_category": module_category,
                    "action": action,
                    "approved": approved,
                },
            )
        status_code = service.http_status_for_result(result)
        logger.audit("web", "run_tool", str(tool_path), status="SUCCESS" if result.ok else "FAILED")
        return jsonify(payload), status_code
    except ProcessRunnerError as e:
        logger.error(f"tool execution rejected: {e}")
        return jsonify(ToolResult.failed(redact_text(str(e))).to_dict()), 400
    except Exception as e:
        logger.error(f"tool execution error: {e}")
        return jsonify(ToolResult.failed(redact_text(str(e))).to_dict()), 500

@app.route('/api/v1/sessions', methods=['GET', 'POST'])
def handle_sessions():
    if request.method == 'GET':
        return jsonify(sessions)
    elif request.method == 'POST':
        session = request.json
        sessions.append(session)
        return jsonify(session), 201

@app.route('/healthz')
def healthz():
    config_valid = config_manager.validate()
    health = {
        "status": "ok" if config_valid else "warn",
        "time": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": int((datetime.now(timezone.utc) - app_start).total_seconds()),
        "checks": {
            "config_valid": config_valid,
            "metrics_file_exists": os.path.exists("logs/metrics.json"),
            "reports_dir_exists": os.path.isdir("reports"),
            "telemetry_enabled": bool(config_manager.get("policy.telemetry_enabled", True)),
        },
    }
    status_code = 200 if health["status"] == "ok" else 503
    return jsonify(health), status_code

@app.route('/metrics')
def metrics():
    payload = metrics_collector.to_prometheus(namespace="blackops")
    return Response(payload, mimetype="text/plain; version=0.0.4")


@app.route('/api/v1/evidence')
def evidence():
    query = request.args.get("q")
    severity = request.args.get("severity")
    category = request.args.get("category")
    limit = int(request.args.get("limit", "25"))
    return jsonify(
        {
            "items": evidence_store.search(query=query, severity=severity, category=category)[:limit],
            "stats": evidence_store.stats(),
        }
    )


@app.route('/api/v1/runs')
def runs():
    limit = int(request.args.get("limit", "10"))
    snapshot = telemetry.snapshot()
    ordered = sorted(snapshot.values(), key=lambda item: item.get("updated_at", ""), reverse=True)
    return jsonify({"items": ordered[:limit], "count": len(snapshot)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
