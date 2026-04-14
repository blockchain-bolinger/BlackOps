
from core.tool_contract import ToolResult, ToolContext
from tools.offensive.airstrike import AirStrike
from typing import Dict

class AirStrikePlugin:
    def __init__(self, context: ToolContext):
        self.context = context
        self.tool = AirStrike()

    def name(self) -> str:
        return "AirStrike"

    def description(self) -> str:
        return "Advanced Network Attack & Penetration Tool"

    def get_parameters(self) -> Dict[str, Dict[str, str]]:
        return {
            "action": {"type": "select", "options": ["scan", "arp", "dos"], "description": "Aktion auswählen"},
            "target": {"type": "str", "description": "Ziel IP/Host"},
            "gateway": {"type": "str", "description": "Gateway IP (nur für ARP)"},
            "port": {"type": "int", "description": "Port (nur für DoS/Scan)"},
            "scan_type": {"type": "select", "options": ["tcp", "udp", "syn"], "description": "Scan-Typ"}
        }

    def run(self, *args, **kwargs) -> ToolResult:
        try:
            action = args[0] if args else kwargs.get("action")
            if action == "scan":
                target = kwargs.get("target")
                if not target:
                    return ToolResult.failed("Missing required parameter: target")
                ports = kwargs.get("ports")
                results = self.tool.port_scan(target, ports, kwargs.get("scan_type", "tcp"))
                return ToolResult.success(data=results)
            
            elif action == "arp":
                if "target" not in kwargs or "gateway" not in kwargs:
                    return ToolResult.failed("Missing required parameters: target and gateway")
                self.tool.arp_spoof(
                    kwargs["target"], 
                    kwargs["gateway"], 
                    kwargs.get("interface", "eth0")
                )
                return ToolResult.success(data="ARP spoofing completed/stopped")
            
            elif action == "dos":
                if "target" not in kwargs or "port" not in kwargs:
                    return ToolResult.failed("Missing required parameters: target and port")
                self.tool.dos_attack(
                    kwargs["target"], 
                    int(kwargs["port"]), 
                    kwargs.get("attack_type", "tcp")
                )
                return ToolResult.success(data="DoS attack completed/stopped")
            
            return ToolResult.failed(f"Unknown action: {action}")
        except Exception as e:
            return ToolResult.failed(str(e))
