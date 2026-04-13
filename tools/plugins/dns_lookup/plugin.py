import socket

from core.plugin_manager import PluginInterface


class DnsLookupPlugin(PluginInterface):
    version = "1.0.0"
    api_version = 1

    def name(self):
        return "dns_lookup"

    def description(self):
        return "Löst einen Hostnamen auf und gibt gefundene IP-Adressen zurück."

    def run(self, **kwargs):
        host = kwargs.get("host")
        if not host:
            raise ValueError("Parameter 'host' ist erforderlich, z.B. host=example.com")

        try:
            infos = socket.getaddrinfo(host, None)
        except socket.gaierror as exc:
            return {"host": host, "addresses": [], "error": str(exc)}

        addresses = sorted({info[4][0] for info in infos if info and info[4]})
        return {"host": host, "addresses": addresses, "count": len(addresses)}

