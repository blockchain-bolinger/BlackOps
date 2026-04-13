import requests
from core.tool_contract import ToolResult, ToolContext
from core.plugin_manager import PluginInterface
from typing import Dict, Any

class DirectoryBruteforcerPlugin(PluginInterface):
    def name(self) -> str:
        return "dir_brute"

    def description(self) -> str:
        return "Directory brute-force scanner"

    def get_parameters(self) -> Dict[str, Dict[str, str]]:
        return {
            "target": {"type": "str", "description": "Target URL (e.g., http://example.com)"},
            "wordlist": {"type": "str", "description": "Wordlist path"}
        }

    def run(self, **kwargs) -> ToolResult:
        target = kwargs.get("target")
        wordlist = kwargs.get("wordlist", "data/wordlists/common_directories.txt")
        results = []
        try:
            with open(wordlist, 'r') as f:
                for line in f:
                    path = line.strip()
                    url = f"{target.rstrip('/')}/{path}"
                    resp = requests.get(url, timeout=2)
                    if resp.status_code == 200:
                        results.append(url)
            return ToolResult.success(data=results)
        except Exception as e:
            return ToolResult.failed(str(e))
