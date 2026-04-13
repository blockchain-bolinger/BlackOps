#!/usr/bin/env python3
"""
Netzwerk-Helferfunktionen.
"""

import ipaddress
import socket
from typing import List


class NetworkUtils:
    @staticmethod
    def validate_ip(value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def resolve_domain(domain: str) -> List[str]:
        try:
            _, _, ips = socket.gethostbyname_ex(domain)
            return list(dict.fromkeys(ips))
        except Exception:
            return []
