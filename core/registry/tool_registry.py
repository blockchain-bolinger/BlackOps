"""
Central tool registry for the Black Ops shell.
"""

from __future__ import annotations

from typing import Any, Dict


BASE_TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "1": {
        "name": "Social Hunter V7 (OSINT Framework)",
        "file": "tools/recon/social_hunter_v7.py",
        "sudo": False,
        "category": "recon",
        "description": "Finds profiles, IPs, phone numbers, and leaked passwords (Findet Profile, IPs, Telefonnummern und geleakte Passwörter)",
    },
    "2": {
        "name": "GhostNet (Anonymity & MAC Changer)",
        "file": "tools/stealth/ghost_net.py",
        "sudo": True,
        "category": "stealth",
        "description": "MAC spoofing, Tor routing, identity checks (MAC-Spoofing, Tor-Routing, Identitäts-Check)",
    },
    "3": {
        "name": "TraceLess (Log Wiper & Cleaner)",
        "file": "tools/stealth/traceless.py",
        "sudo": True,
        "category": "stealth",
        "description": "Removes logs, history, and traces (Löscht Logs, History und Spuren)",
    },
    "4": {
        "name": "NetScout Pro (Reconnaissance)",
        "file": "tools/recon/netscout_pro.py",
        "sudo": False,
        "category": "recon",
        "description": "Port-Scanner, DNS-Enumeration, WAF-Detection",
    },
    "5": {
        "name": "MetaSpy (Image Forensics)",
        "file": "tools/recon/metaspy.py",
        "sudo": False,
        "category": "recon",
        "description": "EXIF data, GPS coordinates, metadata (EXIF-Daten, GPS-Koordinaten, Metadaten)",
    },
    "6": {
        "name": "HashBreaker (Password Cracker)",
        "file": "tools/offensive/hashbreaker.py",
        "sudo": False,
        "category": "offensive",
        "description": "Offline Hash-Cracking (MD5, SHA1, SHA256)",
    },
    "7": {
        "name": "SilentPhish (Cloudflare Phishing)",
        "file": "tools/offensive/silent_phish.py",
        "sudo": False,
        "category": "offensive",
        "description": "Phishing-Server mit Cloudflare-Tunnel",
    },
    "8": {
        "name": "VenomMaker (Payload Generator)",
        "file": "tools/offensive/venom_maker.py",
        "sudo": False,
        "category": "offensive",
        "description": "Reverse/Bind Shells, Downloader, Backdoors",
    },
    "9": {
        "name": "NeuroLink (AI Tactical Advisor)",
        "file": "tools/intelligence/neurolink.py",
        "sudo": False,
        "category": "intelligence",
        "description": "GPT-4o AI for cybersecurity guidance (GPT-4o KI für Cybersecurity-Beratung)",
    },
    "10": {
        "name": "AirStrike (WiFi Jammer & Monitor)",
        "file": "tools/offensive/airstrike.py",
        "sudo": True,
        "category": "offensive",
        "description": "WiFi-Monitoring, Deauth-Attacken",
    },
    "11": {
        "name": "NetShark (ARP Spoofer / MITM)",
        "file": "tools/offensive/netshark.py",
        "sudo": True,
        "category": "offensive",
        "description": "ARP-Spoofing, Man-in-the-Middle",
    },
    "12": {
        "name": "CryptoVault (Decoder/Encoder)",
        "file": "tools/utils/cryptovault.py",
        "sudo": False,
        "category": "utils",
        "description": "Base64, Hashes, ROT13, Encoding/Decoding",
    },
    "13": {
        "name": "System Check & Updates",
        "file": "system_check",
        "sudo": True,
        "category": "utils",
        "description": "Checks system status, updates, and dependencies (System-Status, Updates, Abhängigkeiten prüfen)",
    },
    "14": {
        "name": "Report Generator",
        "file": "report_gen",
        "sudo": False,
        "category": "utils",
        "description": "Exports PDF reports and logs (PDF-Reports, Logs exportieren)",
    },
    "15": {
        "name": "WebHunter (Web Vulnerability Scanner)",
        "file": "tools/recon/webhunter.py",
        "sudo": False,
        "category": "offensive",
        "description": "SQLi, XSS, LFI, SSRF, Command Injection Scanner",
    },
    "16": {
        "name": "SubScout (Subdomain Enumeration)",
        "file": "tools/recon/subscout.py",
        "sudo": False,
        "category": "recon",
        "description": "Subdomain Bruteforce, CT Logs, Takeover Check",
    },
    "17": {
        "name": "CloudRaider (Cloud Security Check)",
        "file": "tools/offensive/cloudraider.py",
        "sudo": False,
        "category": "offensive",
        "description": "Checks AWS S3, Azure Blob, and GCP buckets for public access (Prüft AWS S3, Azure Blob, GCP Buckets auf öffentlichen Zugriff)",
    },
    "18": {
        "name": "MobileSpy (App Security Analyzer)",
        "file": "tools/recon/mobilespy.py",
        "sudo": False,
        "category": "recon",
        "description": "Analyzes APK/IPA for secrets and insecure configurations (APK/IPA Analyse auf Secrets, unsichere Konfigurationen)",
    },
    "19": {
        "name": "CredCannon (Brute-Force Suite)",
        "file": "tools/offensive/credcannon.py",
        "sudo": False,
        "category": "offensive",
        "description": "Multi-Protocol Brute-Force (SSH, FTP, MySQL, HTTP Basic)",
    },
    "20": {
        "name": "DarkWebMonitor (Tor Crawler)",
        "file": "tools/intelligence/darkwebmonitor.py",
        "sudo": False,
        "category": "intelligence",
        "description": ".onion crawler and leak search (Tor required / Tor erforderlich)",
    },
    "21": {
        "name": "CodeDigger (Secret Scanner)",
        "file": "tools/recon/codedigger.py",
        "sudo": False,
        "category": "recon",
        "description": "Searches GitHub/GitLab for API keys and passwords (GitHub/GitLab nach API-Keys, Passwörtern durchsuchen)",
    },
    "22": {
        "name": "MailTracker (Email Security)",
        "file": "tools/recon/mailtracker.py",
        "sudo": False,
        "category": "recon",
        "description": "SPF, DKIM, DMARC, tracking pixel analysis (SPF, DKIM, DMARC, Tracking-Pixel Analyse)",
    },
    "23": {
        "name": "LogShield (Log Monitor)",
        "file": "tools/stealth/logshield.py",
        "sudo": True,
        "category": "stealth",
        "description": "Real-time log monitoring with alerts (Echtzeit-Log-Überwachung mit Alarmfunktion)",
    },
    "24": {
        "name": "Decryptor (Encoding Toolkit)",
        "file": "tools/utils/decryptor.py",
        "sudo": False,
        "category": "utils",
        "description": "Base64, ROT13, Hashes, AES, JWT Decoding",
    },
    "25": {
        "name": "OSINT Username (Specialized)",
        "file": "tools/recon/osint_username.py",
        "sudo": False,
        "category": "recon",
        "description": "Focused lookup for username/nickname across configured social sites",
    },
    "26": {
        "name": "OSINT Email (Specialized)",
        "file": "tools/recon/osint_email.py",
        "sudo": False,
        "category": "recon",
        "description": "Focused email intelligence: breach lookup, domain context, search links",
    },
    "27": {
        "name": "OSINT Phone (Specialized)",
        "file": "tools/recon/osint_phone.py",
        "sudo": False,
        "category": "recon",
        "description": "Focused phone-number intelligence with normalized output and pivot links",
    },
    "28": {
        "name": "OSINT IP (Specialized)",
        "file": "tools/recon/osint_ip.py",
        "sudo": False,
        "category": "recon",
        "description": "Focused IP intelligence: geodata, reverse DNS, open-source pivots",
    },
    "29": {
        "name": "OSINT Domain (Specialized)",
        "file": "tools/recon/osint_domain.py",
        "sudo": False,
        "category": "recon",
        "description": "Focused domain intelligence: DNS, RDAP and certificate-based subdomains",
    },
    "30": {
        "name": "OSINT Person (First + Last Name)",
        "file": "tools/recon/osint_person.py",
        "sudo": False,
        "category": "recon",
        "description": "Focused person lookup using first and last name with pivot generation",
    },
    "99": {
        "name": "Exit / Self-Destruct",
        "file": "exit",
        "sudo": False,
        "category": "system",
        "description": "Safely exits the framework (Beendet Framework sicher)",
    },
}


DEFAULT_CATEGORIES: Dict[str, str] = {
    "recon": "🔍 RECON & OSINT",
    "offensive": "⚔️ OFFENSIVE & NETWORK",
    "stealth": "👻 STEALTH & UTILS",
    "intelligence": "🧠 INTELLIGENCE",
    "utils": "🛠️ SYSTEM & UTILS",
    "system": "🚪 SYSTEM",
}


def build_tool_registry(plugins: Dict[str, Any]) -> tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
    tools = {tool_id: dict(tool_data) for tool_id, tool_data in BASE_TOOL_REGISTRY.items()}
    plugin_id = 100
    for name, instance in sorted(plugins.items(), key=lambda item: item[0].lower()):
        tools[str(plugin_id)] = {
            "name": f"{name} (Plugin)",
            "file": "plugin",
            "sudo": False,
            "category": "utils",
            "description": instance.description(),
        }
        plugin_id += 1
    return tools, dict(DEFAULT_CATEGORIES)
