# Black Ops Framework v2.2

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)
![Version](https://img.shields.io/badge/Version-2.2-orange)

Black Ops ist ein modulares Cybersecurity-Framework fuer autorisierte Sicherheitspruefungen. Diese README dokumentiert die praktische Nutzung aller vorhandenen Tools und Plugins im aktuellen Repo-Stand.

## Rechtlicher Hinweis

Dieses Framework darf nur mit ausdruecklicher Genehmigung verwendet werden.

Erlaubt:
- Eigene Systeme/Labs
- CTF-Umgebungen
- Autorisierte Penetration Tests

Verboten:
- Unautorisierte Angriffe
- Jede illegale Nutzung

## Installation

```bash
chmod +x install.sh
./install.sh
```

Start:

```bash
./run.sh
```

Alternativ:

```bash
python3 black_ops.py
```

## Bedienmodi

Es gibt 3 praktische Wege:

1. Hauptanwendung (Menue): `python3 black_ops.py`
2. Profil-/Batch-CLI: `python3 black_ops.py <subcommand> ...`
3. Interaktive Shell: `python3 black_ops_cli.py`

## Globaler CLI-Einstieg (`black_ops.py`)

```bash
python3 black_ops.py --help
```

Wichtige Profile:

```bash
python3 black_ops.py scan --tool tools.recon.netscout_pro
python3 black_ops.py scan --tool tools.recon.netscout_pro --dry-run

python3 black_ops.py report --target example.com --format json
python3 black_ops.py report --target example.com --format md --dry-run

python3 black_ops.py c2 --action status
python3 black_ops.py payload --action list

python3 black_ops.py config --action lint
python3 black_ops.py config --action doctor
python3 black_ops.py config --action migrate --target-version 2.2
```

## Interaktive Shell (`black_ops_cli.py`)

Start:

```bash
python3 black_ops_cli.py
```

Wichtige Befehle:

- `show tools` listet alle Python-Toolmodule unter `tools/`
- `show plugins` listet alle geladenen Plugins inkl. Status
- `use <tool-pfad>` waehlt ein Tool (Beispiel: `use tools/recon/netscout.py`)
- `set KEY VALUE` setzt Tool-Optionen (nur wenn Tool `main(options)` erwartet)
- `run [--dry-run]` startet das aktive Tool
- `plugin run <name> KEY=VALUE ... [--dry-run]` startet ein Plugin
- `back` setzt den Tool-Kontext zurueck
- `exit` beendet die Shell

Beispiele:

```bash
show tools
show plugins
plugin run sys_info
plugin run dns_lookup host=example.com
plugin run file_hash path=README.md algo=sha256
```

## Tool-Katalog

Hinweis: Nicht jedes Modul ist direkt im Hauptmenue verdrahtet. Alle Module koennen aber direkt per Python (oder in vielen Faellen ueber `scan --tool ...`) gestartet werden.

### Recon Tools

#### 1) `tools.recon.social_hunter_v7`

Zweck:
- Username- und E-Mail-OSINT (inkl. optionaler API-basierter Leak-Checks)

Aufruf:

```bash
# Menue: Recon -> Social Hunter v7
python3 black_ops.py scan --tool tools.recon.social_hunter_v7

# Direkt
python3 tools/recon/social_hunter_v7.py <target> -t username -o report.txt
python3 tools/recon/social_hunter_v7.py user@example.com -t email
```

Parameter (direkt):
- `target`: Username oder E-Mail
- `-t/--type`: `username|email`
- `-o/--output`: optionaler Report-Pfad

API-Keys (optional fuer Breach-Checks):
- `haveibeenpwned`
- `dehashed`

In `secrets.json` moeglich ueber:
- `api_keys.haveibeenpwned`
- `api_keys.dehashed`

#### 2) `tools.recon.netscout_pro`

Zweck:
- Header-Analyse, Subdomain-Bruteforce, schneller Portscan, JSON-Export

Aufruf:

```bash
# Menue: Recon -> NetScout Pro
python3 black_ops.py scan --tool tools.recon.netscout_pro

# Direkt
python3 tools/recon/netscout_pro.py example.com -t 30 -o netscout_pro.json
```

Parameter:
- `target` Domain/Host
- `-t/--threads` Threadanzahl
- `-o/--output` JSON-Datei

#### 3) `tools.recon.metaspy`

Zweck:
- EXIF- und GPS-Analyse von Bildern

Aufruf:

```bash
# Menue: Recon -> MetaSpy
python3 black_ops.py scan --tool tools.recon.metaspy

# Direkt interaktiv
python3 tools/recon/metaspy.py
```

Ablauf:
- Bildpfad eingeben
- Metadaten/GPS werden ausgegeben
- optionaler Maps-Link bei vorhandenen Koordinaten

#### 4) `tools.recon.netscout` (direkt)

Zweck:
- Basis-Recon: HTTP-Header, DNS-Records, optionale Portpruefung

Aufruf:

```bash
python3 tools/recon/netscout.py example.com --scan-ports
python3 tools/recon/netscout.py example.com -v
```

#### 5) `tools.recon.shodan_search` (direkt)

Zweck:
- Shodan-Suche (benoetigt Shodan-Key)

Aufruf:

```bash
python3 tools/recon/shodan_search.py "apache country:DE"
```

Voraussetzung:
- `shodan` Python-Paket
- API-Key in `secrets.json`/Umgebung

### Offensive Tools

#### 1) `tools.offensive.airstrike`

Zweck:
- Portscan, ARP-Test, Last-/DoS-Test in autorisierten Testumgebungen

Aufruf:

```bash
# Menue: Offensive -> AirStrike
python3 black_ops.py scan --tool tools.offensive.airstrike

# Direkt
python3 tools/offensive/airstrike.py scan 192.168.1.10 -p 1-1024 -t tcp
python3 tools/offensive/airstrike.py arp 192.168.1.20 192.168.1.1 -i eth0
python3 tools/offensive/airstrike.py dos 192.168.1.10 80 -t http
```

#### 2) `tools.offensive.netshark`

Zweck:
- ARP-Manipulations-/MITM-Test mit Wiederherstellungslogik

Aufruf:

```bash
# Menue: Offensive -> NetShark
python3 black_ops.py scan --tool tools.offensive.netshark

# Direkt (root erforderlich)
sudo python3 tools/offensive/netshark.py
```

#### 3) `tools.offensive.silent_phish`

Zweck:
- Simulierter Credential-Capture-Webflow fuer Awareness/Lab-Tests

Aufruf:

```bash
# Menue: Offensive -> Silent Phish
python3 black_ops.py scan --tool tools.offensive.silent_phish

# Direkt
python3 tools/offensive/silent_phish.py
```

Ablauf:
- optional Tunnel starten
- lokalen Server starten
- Eingaben landen in `loot.txt`

#### 4) `tools.offensive.venom_maker`

Zweck:
- Payload-Generator mit mehreren Templates und Obfuscation-Stufen

Aufruf:

```bash
# Menue: Offensive -> Venom Maker
python3 black_ops.py scan --tool tools.offensive.venom_maker

# Direkt
python3 tools/offensive/venom_maker.py
```

Ablauf:
- Ethik-Bestaetigung
- Payload-Typ waehlen
- Plattform/Obfuscation/Optionen konfigurieren
- Datei wird generiert

#### 5) `tools.offensive.hashbreaker`

Zweck:
- Offline Dictionary Hash-Cracking (md5/sha1/sha256)

Aufruf:

```bash
# Menue: Offensive -> HashBreaker
python3 black_ops.py scan --tool tools.offensive.hashbreaker

# Direkt
python3 tools/offensive/hashbreaker.py
```

Eingaben:
- Algorithmus
- Ziel-Hash
- Wordlist-Pfad (Default rockyou)

#### 6) `tools.offensive.exploit_launcher` (direkt)

Zweck:
- Suche/Download von ExploitDB-Eintraegen via `searchsploit`

Aufruf:

```bash
python3 tools/offensive/exploit_launcher.py search openssl
python3 tools/offensive/exploit_launcher.py run <EDB-ID> <TARGET_IP>
```

Voraussetzung:
- `searchsploit` installiert

### Stealth Tools

#### 1) `tools.stealth.ghost_net`

Zweck:
- Stealth-HTTP-Requests, IP-Check, Proxy-/Tor-Nutzung

Aufruf:

```bash
# Menue: Stealth -> Ghost Net
python3 black_ops.py scan --tool tools.stealth.ghost_net

# Direkt
python3 tools/stealth/ghost_net.py ip
python3 tools/stealth/ghost_net.py ip --tor
python3 tools/stealth/ghost_net.py proxy -f data/configs/proxies.txt
python3 tools/stealth/ghost_net.py request https://example.com -m GET -d 1.5 --tor
```

#### 2) `tools.stealth.traceless`

Zweck:
- Log-/History-Cleaning-Funktionen (nur in kontrollierten Testsystemen)

Aufruf:

```bash
# Menue: Stealth -> Traceless
python3 black_ops.py scan --tool tools.stealth.traceless

# Direkt (root erforderlich)
sudo python3 tools/stealth/traceless.py
```

### Intelligence Tools

#### 1) `tools.intelligence.neurolink`

Zweck:
- AI-Berater ueber OpenAI API

Aufruf:

```bash
# Menue: Intelligence -> NeuroLink
python3 black_ops.py scan --tool tools.intelligence.neurolink

# Direkt
python3 tools/intelligence/neurolink.py
```

Voraussetzung:
- `openai` Paket
- gueltiger `openai_key` in `secrets.json`

### Utility Tools

#### 1) `tools.utils.cryptovault`

Zweck:
- Base64 Encode/Decode, Hashing, ROT13

Aufruf:

```bash
# Menue: Utility -> CryptoVault
python3 black_ops.py scan --tool tools.utils.cryptovault

# Direkt
python3 tools/utils/cryptovault.py
```

#### 2) `tools.utils.file_analyzer`

Zweck:
- Datei-MIME, Groesse, Executable-Check, SHA256

Aufruf:

```bash
# Menue: Utility -> File Analyzer
python3 black_ops.py scan --tool tools.utils.file_analyzer

# Direkt
python3 tools/utils/file_analyzer.py
```

#### 3) `tools.utils.network_scanner`

Zweck:
- schneller Multiport-TCP-Check

Aufruf:

```bash
# Menue: Utility -> Network Scanner
python3 black_ops.py scan --tool tools.utils.network_scanner

# Direkt
python3 tools/utils/network_scanner.py
```

#### 4) `tools.utils.system_info`

Zweck:
- System-Basisinfos (OS, Hostname, IP, User)

Aufruf:

```bash
# Menue: Utility -> System Info
python3 black_ops.py scan --tool tools.utils.system_info

# Direkt
python3 tools/utils/system_info.py
```

#### 5) `tools.utils.evasion` (Library)

Zweck:
- Hilfsfunktionen fuer Obfuscation/Mutation

Nutzung als Import:

```python
from tools.utils.evasion import Evasion

payload = "print('hello')"
enc = Evasion.base64_obfuscate(payload)
```

### Wireless Tools (derzeit nicht im Hauptmenue verdrahtet)

#### 1) `tools.wireless.wifi_scanner`

```bash
python3 tools/wireless/wifi_scanner.py
```

- nutzt `airodump-ng`
- schreibt temporaer nach `/tmp/airodump-01.csv`

#### 2) `tools.wireless.bluetooth_scanner`

```bash
python3 tools/wireless/bluetooth_scanner.py
```

- nutzt `hcitool scan`

#### 3) `tools.wireless.handshake_capture`

```bash
python3 tools/wireless/handshake_capture.py <interface> <bssid> <channel>
```

- aktiviert Monitor-Mode
- Captures fuer definiertes Timeout

#### 4) `tools.wireless.deauth_attack`

```bash
python3 tools/wireless/deauth_attack.py <BSSID> [interface]
```

- startet `aireplay-ng` mit Deauth-Frames

## Plugin-System

Plugin-Pfad:
- `tools/plugins/<plugin_name>/plugin.py` oder `tools/plugins/<plugin_name>.py`

Interaktive Shell:

```bash
python3 black_ops_cli.py
show plugins
plugin run <plugin_name> KEY=VALUE ...
```

### Verfuegbare Plugins

#### 1) `example_plugin`

```bash
plugin run ExamplePlugin
plugin run ExamplePlugin foo=bar
```

#### 2) `sys_info`

Zweck:
- Laufzeit-/Systeminfos

```bash
plugin run sys_info
plugin run sys_info env_keys=HOME,USER,SHELL
```

Parameter:
- `env_keys` CSV-Liste von Umgebungsvariablen

#### 3) `dns_lookup`

Zweck:
- DNS-Aufloesung von Hostnamen

```bash
plugin run dns_lookup host=example.com
```

Parameter:
- `host` (erforderlich)

#### 4) `file_hash`

Zweck:
- Datei-Hashing

```bash
plugin run file_hash path=README.md
plugin run file_hash path=README.md algo=sha512
```

Parameter:
- `path` (erforderlich)
- `algo` optional: `sha256` (default), `sha512`, `sha1`, `md5`

#### 5) `secrets_leak_check`

Zweck:
- Source-/Text-Scan auf moegliche Secret-Leaks

```bash
plugin run secrets_leak_check
plugin run secrets_leak_check path=. include=*.py,*.env,*.json
plugin run secrets_leak_check path=. exclude=venv,.git,reports
plugin run secrets_leak_check path=. rules=strict workers=4 respect_gitignore=true
plugin run secrets_leak_check path=. fail_on_findings=true exit_code=2
plugin run secrets_leak_check path=. baseline=.blackops/secrets-baseline.json
plugin run secrets_leak_check path=. baseline=.blackops/secrets-baseline.json write_baseline=true
plugin run secrets_leak_check path=. rules_file=custom_rules.json
```

Wichtige Parameter:
- `path` Scan-Root (default `.`)
- `include` CSV-Globliste
- `exclude` CSV-Pfadteile
- `max_files` default `2000`
- `max_file_size_kb` default `256`
- `workers` default `1`
- `respect_gitignore` `true|false`
- `rules` `default|strict`
- `rules_file` JSON-Regeldatei
- `baseline` Pfad zu Fingerprint-Baseline
- `write_baseline` `true|false`
- `fail_on_findings` `true|false`
- `exit_code` default `2`

`custom_rules.json` Beispiel:

```json
{
  "rules": [
    {
      "name": "internal_token",
      "pattern": "internal_token\\s*=\\s*['\"][^'\"]+['\"]",
      "flags": "i"
    }
  ]
}
```

#### 6) `osint_domain_profile`

Zweck:
- Domain-OSINT-Profil (DNS, TLS, HTTP-Header, Titel)

```bash
plugin run osint_domain_profile domain=example.com
plugin run osint_domain_profile domain=example.com timeout=8
```

Parameter:
- `domain` (erforderlich)
- `timeout` optional (Sekunden)

#### 7) `osint_username_probe`

Zweck:
- Username-Existenzpruefung auf mehreren Plattformen

```bash
plugin run osint_username_probe username=octocat
plugin run osint_username_probe username=octocat sites=github,reddit,gitlab timeout=8
```

Parameter:
- `username` (erforderlich)
- `sites` CSV-Auswahl (default: alle bekannten)
- `timeout` optional

Bekannte `sites`:
- `github`, `gitlab`, `reddit`, `medium`, `devto`, `pinterest`

#### 8) `osint_email_footprint`

Zweck:
- Basisprofil zu E-Mail (Domain-Aufloesung + Gravatar-Hash)

```bash
plugin run osint_email_footprint email=user@example.com
```

Parameter:
- `email` (erforderlich)

## Troubleshooting

1. Abhaengigkeiten fehlen

```bash
./install.sh
# oder gezielt
pip install -r requirements.txt
```

2. Tool startet nicht aus Menue
- pruefe Modulpfad
- pruefe Python-Abhaengigkeiten des Moduls
- nutze `--dry-run`, um Aufruf zu validieren

3. Plugin wird nicht gefunden
- liegt Datei unter `tools/plugins/...`?
- gibt es eine Klasse, die `PluginInterface` erweitert?
- pruefe mit `show plugins`

4. Rechteprobleme
- einige Module benoetigen Root (z. B. Netzwerk/Wireless)

## Tests

```bash
python -m unittest discover -s tests
```

Nur Unit-Tests:

```bash
python -m unittest discover -s tests/unit_tests -v
```

## Sensible Dateien

Nicht mit echten Geheimnissen committen:
- `secrets.json`
- `.env`
- `blackops_config.json`

Report-/Log-Ausgaben:
- `logs/`
- `reports/`

