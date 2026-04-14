#!/usr/bin/env python3
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, request, Response
import os
from pathlib import Path

from core.config_manager import ConfigManager
from core.execution_service import ExecutionService
from core.metrics import MetricsCollector
from core.process_runner import SafeProcessRunner, ProcessRunnerError
from core.redaction_utils import redact_data, redact_text
from core.tool_contract import ToolResult

app = Flask(__name__)
app_start = datetime.now(timezone.utc)
config_manager = ConfigManager()
metrics_collector = MetricsCollector()
base_dir = Path.cwd().resolve()
tools_dir = (base_dir / "tools").resolve()
process_runner = SafeProcessRunner(allowed_roots=[base_dir, tools_dir])


def _build_execution_service():
    return ExecutionService(
        process_runner=process_runner,
        base_dir=base_dir,
        tools_dir=tools_dir,
    )

# In-Memory "Datenbank" für Sessions
sessions = []

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

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

    try:
        timeout = config_manager.get("runtime.task_timeout_seconds", 30)
        service = _build_execution_service()
        result = service.execute_tool(
            tool_path,
            args=args,
            timeout=timeout,
            cwd=base_dir,
            capture_output=True,
        )
        payload = result.to_dict()
        payload["errors"] = [redact_text(str(item)) for item in payload.get("errors", [])]
        if isinstance(payload.get("data"), dict):
            payload["data"] = redact_data(payload["data"])
        status_code = service.http_status_for_result(result)
        return jsonify(payload), status_code
    except ProcessRunnerError as e:
        return jsonify(ToolResult.failed(redact_text(str(e))).to_dict()), 400
    except Exception as e:
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
    health = {
        "status": "ok" if config_manager.validate() else "warn",
        "time": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": int((datetime.now(timezone.utc) - app_start).total_seconds()),
        "checks": {
            "config_valid": config_manager.validate(),
            "metrics_file_exists": os.path.exists("logs/metrics.json"),
            "reports_dir_exists": os.path.isdir("reports"),
        },
    }
    status_code = 200 if health["status"] == "ok" else 503
    return jsonify(health), status_code

@app.route('/metrics')
def metrics():
    payload = metrics_collector.to_prometheus(namespace="blackops")
    return Response(payload, mimetype="text/plain; version=0.0.4")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
