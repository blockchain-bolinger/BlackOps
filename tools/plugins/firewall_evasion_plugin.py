from scapy.all import IP, TCP, sr1
from core.tool_contract import ToolResult
from core.plugin_manager import PluginInterface
from typing import Dict, Any

class FirewallEvasionPlugin(PluginInterface):
    def name(self) -> str:
        return "firewall_evasion"

    def description(self) -> str:
        return "Scan with non-standard TCP flags"

    def get_parameters(self) -> Dict[str, Dict[str, str]]:
        return {
            "target": {"type": "str", "description": "Target IP"},
            "port": {"type": "int", "description": "Port"}
        }

    def run(self, **kwargs) -> ToolResult:
        target = kwargs.get("target")
        port = int(kwargs.get("port", 80))
        try:
            # XMAS scan (FIN, URG, PSH)
            packet = IP(dst=target)/TCP(dport=port, flags="FPU")
            response = sr1(packet, timeout=1, verbose=0)
            status = "open|filtered" if response is None else "closed"
            return ToolResult.success(data={"status": status})
        except Exception as e:
            return ToolResult.failed(str(e))
