"""
Report Generator für Black Ops Framework mit einheitlichem Schema.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
from core.tool_contract import ToolResult
from core.redaction_utils import redact_data, redact_text
from core.evidence_store import EvidenceStore

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


SEVERITY_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
PLAYBOOK_BY_CATEGORY = {
    "injection": "playbooks/injection.md",
    "xss": "playbooks/xss.md",
    "auth": "playbooks/authentication.md",
    "exposure": "playbooks/data_exposure.md",
    "network": "playbooks/network_hardening.md",
    "default": "playbooks/general_remediation.md",
}
CWE_BY_KEYWORD = {
    "sql": "CWE-89",
    "xss": "CWE-79",
    "csrf": "CWE-352",
    "ssrf": "CWE-918",
    "auth": "CWE-287",
    "exposure": "CWE-200",
    "command": "CWE-78",
    "path traversal": "CWE-22",
}


class ReportGenerator:
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _classify_category(self, title: str, description: str) -> str:
        text = f"{title} {description}".lower()
        if "sql" in text or "inject" in text:
            return "injection"
        if "xss" in text:
            return "xss"
        if "auth" in text or "login" in text or "password" in text:
            return "auth"
        if "exposure" in text or "leak" in text or "sensitive" in text:
            return "exposure"
        return "network"

    def _infer_cwe(self, title: str, description: str) -> str:
        text = f"{title} {description}".lower()
        for key, cwe in CWE_BY_KEYWORD.items():
            if key in text:
                return cwe
        return "CWE-Other"

    def _normalize_cves(self, item: Dict[str, Any]) -> List[str]:
        cves = item.get("cve") or item.get("cves") or []
        if isinstance(cves, str):
            cves = [cves]
        if not isinstance(cves, list):
            return []
        return [str(cve) for cve in cves if str(cve).strip()]

    def _risk_score(self, severity: str, cves: List[str], has_evidence: bool) -> float:
        base = {"critical": 9.0, "high": 7.5, "medium": 5.0, "low": 3.0, "info": 1.0}.get(severity, 1.0)
        bonus = min(1.0, 0.2 * len(cves))
        evidence_bonus = 0.5 if has_evidence else 0.0
        return round(min(10.0, base + bonus + evidence_bonus), 1)

    def _normalize_findings(self, findings: List[Dict[str, Any] | ToolResult]) -> List[Dict[str, Any]]:
        normalized = []
        for item in findings or []:
            # Falls das Item ein ToolResult Objekt ist, extrahiere die Daten
            if hasattr(item, "data"):
                # Angenommen, data enthält die Findings-Liste oder ein einzelnes Finding
                item = item.data if isinstance(item.data, dict) else {"vulnerability": str(item.data)}
            
            severity = str(item.get("severity", "info")).lower()
            title = item.get("vulnerability") or item.get("title", "Unknown finding")
            description = item.get("description", "")
            category = item.get("category") or self._classify_category(title, description)
            cwe = item.get("cwe") or self._infer_cwe(title, description)
            cves = self._normalize_cves(item)
            evidence = item.get("evidence", [])
            playbook = item.get("playbook") or PLAYBOOK_BY_CATEGORY.get(category, PLAYBOOK_BY_CATEGORY["default"])
            normalized.append(
                {
                    "id": item.get("id") or f"finding-{len(normalized)+1}",
                    "severity": severity,
                    "title": title,
                    "description": description,
                    "category": category,
                    "cwe": cwe,
                    "cves": cves,
                    "risk_score": self._risk_score(severity, cves, has_evidence=bool(evidence)),
                    "risk": item.get("risk", ""),
                    "remediation": item.get("remediation", "No remediation hint provided."),
                    "playbook": playbook,
                    "evidence": evidence,
                }
            )
        normalized.sort(key=lambda x: SEVERITY_WEIGHT.get(x["severity"], 0), reverse=True)
        return normalized

    def _severity_summary(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {level: 0 for level in ["critical", "high", "medium", "low", "info"]}
        for finding in findings:
            summary[finding["severity"]] = summary.get(finding["severity"], 0) + 1
        return summary

    def _build_schema(self, report_type: str, data: Dict[str, Any], report_id: str) -> Dict[str, Any]:
        findings = self._normalize_findings(data.get("findings", []))
        schema = {
            "schema_version": "1.0",
            "report_type": report_type,
            "report_id": report_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "target": redact_text(str(data.get("target", "N/A"))),
                "tester": redact_text(str(data.get("tester", "N/A"))),
                "scope": redact_text(str(data.get("scope", "N/A"))),
                "tools_used": redact_data(data.get("tools_used", [])),
            },
            "summary": {
                "executive_summary": redact_text(str(data.get("executive_summary", "No summary provided."))),
                "severity": self._severity_summary(findings),
                "total_findings": len(findings),
                "average_risk_score": round(
                    (sum(f.get("risk_score", 0.0) for f in findings) / len(findings)) if findings else 0.0, 2
                ),
            },
            "findings": findings,
            "recommendations": redact_data(data.get("recommendations", [])),
            "technical_details": redact_data(data.get("technical_details", {})),
        }
        return redact_data(schema)

    def generate_pentest_report(
        self,
        data: Dict[str, Any],
        format: str = "pdf",
        evidence_store: EvidenceStore | None = None,
    ) -> str:
        report_id = f"pentest_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        report = self._build_schema("pentest", data, report_id)
        path = self._write_report(report, format=format, subdir="pentest")
        self._persist_evidence(report, source_tool="report:pentest", evidence_store=evidence_store)
        return path

    def generate_vulnerability_report(
        self,
        scan_data: Dict[str, Any],
        evidence_store: EvidenceStore | None = None,
    ) -> str:
        report_id = f"vuln_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        report = self._build_schema("vulnerability", scan_data, report_id)
        path = self._write_report(report, format="json", subdir="scans")
        self._persist_evidence(report, source_tool="report:vulnerability", evidence_store=evidence_store)
        return path

    def generate_delta_report(self, previous_report_path: str, current_report_path: str, format: str = "json") -> str:
        with open(previous_report_path, "r", encoding="utf-8") as handle:
            previous = json.load(handle)
        with open(current_report_path, "r", encoding="utf-8") as handle:
            current = json.load(handle)

        prev_ids = {f.get("id"): f for f in previous.get("findings", [])}
        curr_ids = {f.get("id"): f for f in current.get("findings", [])}

        added = [curr_ids[x] for x in curr_ids.keys() - prev_ids.keys()]
        removed = [prev_ids[x] for x in prev_ids.keys() - curr_ids.keys()]

        changed = []
        for fid in prev_ids.keys() & curr_ids.keys():
            if prev_ids[fid] != curr_ids[fid]:
                changed.append({"id": fid, "before": prev_ids[fid], "after": curr_ids[fid]})

        delta = {
            "schema_version": "1.0",
            "report_type": "delta",
            "report_id": f"delta_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "previous_report": str(previous_report_path),
                "current_report": str(current_report_path),
            },
            "summary": {
                "added": len(added),
                "removed": len(removed),
                "changed": len(changed),
            },
            "changes": {
                "added": added,
                "removed": removed,
                "changed": changed,
            },
        }
        return self._write_report(delta, format=format, subdir="delta")

    def _write_report(self, report: Dict[str, Any], format: str, subdir: str) -> str:
        destination = self.reports_dir / subdir
        destination.mkdir(parents=True, exist_ok=True)
        report = redact_data(report)
        report_id = report["report_id"]
        fmt = format.lower()
        if fmt == "json":
            return self._write_json(destination / f"{report_id}.json", report)
        if fmt == "html":
            return self._write_html(destination / f"{report_id}.html", report)
        if fmt in {"md", "markdown"}:
            return self._write_markdown(destination / f"{report_id}.md", report)
        if fmt == "pdf":
            return self._write_pdf(destination / f"{report_id}.pdf", report)
        return self._write_markdown(destination / f"{report_id}.md", report)

    def _persist_evidence(self, report: Dict[str, Any], source_tool: str, evidence_store: EvidenceStore | None) -> None:
        if evidence_store is None:
            return
        target = str(report.get("metadata", {}).get("target", ""))
        profile = str(report.get("metadata", {}).get("profile", "report"))
        correlation_id = str(report.get("metadata", {}).get("correlation_id", "-"))
        run_id = str(report.get("report_id", "-"))
        for finding in report.get("findings", []):
            if isinstance(finding, dict):
                evidence_store.ingest_finding(
                    source_tool=source_tool,
                    profile=profile,
                    correlation_id=correlation_id,
                    run_id=run_id,
                    finding=finding,
                    target=target,
                    metadata={"report_id": report.get("report_id"), "report_type": report.get("report_type")},
                )

    def _write_json(self, path: Path, data: Dict[str, Any]) -> str:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        return str(path)

    def _write_html(self, path: Path, report: Dict[str, Any]) -> str:
        rows = []
        for finding in report.get("findings", []):
            rows.append(
                "<tr>"
                f"<td>{finding.get('severity')}</td>"
                f"<td>{finding.get('title')}</td>"
                f"<td>{finding.get('description')}</td>"
                f"<td>{finding.get('cwe')}</td>"
                f"<td>{', '.join(finding.get('cves', []))}</td>"
                f"<td>{finding.get('risk_score')}</td>"
                f"<td>{finding.get('risk')}</td>"
                f"<td>{finding.get('remediation')}</td>"
                f"<td>{finding.get('playbook')}</td>"
                "</tr>"
            )
        html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{report['report_id']}</title></head>
<body>
<h1>{report['report_type'].title()} Report</h1>
<p>Target: {report['metadata'].get('target', 'N/A')}</p>
<p>Tester: {report['metadata'].get('tester', 'N/A')}</p>
<h2>Executive Summary</h2>
<p>{report['summary'].get('executive_summary', '')}</p>
<h2>Findings</h2>
<table border="1" cellspacing="0" cellpadding="6">
<tr><th>Severity</th><th>Finding</th><th>Description</th><th>CWE</th><th>CVE</th><th>Risk Score</th><th>Risk</th><th>Remediation</th><th>Playbook</th></tr>
{''.join(rows)}
</table>
</body></html>"""
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(html)
        return str(path)

    def _write_markdown(self, path: Path, report: Dict[str, Any]) -> str:
        lines = [
            f"# {report['report_type'].title()} Report",
            "",
            f"- Report ID: {report['report_id']}",
            f"- Generated: {report['generated_at']}",
            f"- Target: {report['metadata'].get('target', 'N/A')}",
            "",
            "## Executive Summary",
            report["summary"].get("executive_summary", ""),
            "",
            "## Findings",
            "| Severity | Finding | Description | CWE | CVE | Risk Score | Risk | Remediation | Playbook |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for finding in report.get("findings", []):
            lines.append(
                f"| {finding.get('severity')} | {finding.get('title')} | {finding.get('description')} | "
                f"{finding.get('cwe')} | {', '.join(finding.get('cves', []))} | {finding.get('risk_score')} | "
                f"{finding.get('risk')} | {finding.get('remediation')} | {finding.get('playbook')} |"
            )
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
        return str(path)

    def _write_pdf(self, path: Path, report: Dict[str, Any]) -> str:
        if not REPORTLAB_AVAILABLE:
            return self._write_markdown(path.with_suffix(".md"), report)
        doc = SimpleDocTemplate(str(path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"{report['report_type'].title()} Report", styles["Title"]),
            Spacer(1, 12),
            Paragraph(f"Report ID: {report['report_id']}", styles["Normal"]),
            Paragraph(f"Target: {report['metadata'].get('target', 'N/A')}", styles["Normal"]),
            Spacer(1, 12),
            Paragraph("Executive Summary", styles["Heading2"]),
            Paragraph(report["summary"].get("executive_summary", ""), styles["Normal"]),
            Spacer(1, 12),
            Paragraph("Findings", styles["Heading2"]),
        ]
        for finding in report.get("findings", []):
            story.append(
                Paragraph(
                    f"- [{finding['severity'].upper()}] {finding['title']} "
                    f"(CWE: {finding.get('cwe')}, Risk: {finding.get('risk_score')})",
                    styles["Normal"],
                )
            )
            story.append(Paragraph(f"  Remediation: {finding['remediation']}", styles["Normal"]))
            story.append(Paragraph(f"  Playbook: {finding.get('playbook')}", styles["Normal"]))
        doc.build(story)
        return str(path)
