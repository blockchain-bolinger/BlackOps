# Black Ops Framework v2.2
**Python License Platform Version**
Black Ops is a modular cybersecurity framework for authorized security assessments. This README documents the practical use of all available tools and plugins in the current repository state.
### Legal Notice
This framework may only be used with explicit permission.
**Permitted:**
 * Own systems/labs
 * CTF environments
 * Authorized penetration tests
**Prohibited:**
 * Unauthorized attacks
 * Any illegal use
## Installation
```bash
chmod +x install.sh
./install.sh

```
**Start:**
```bash
./run.sh

```
**Alternatively:**
```bash
python3 black_ops.py

```
## Operating Modes
There are 3 practical ways to use the framework:
 1. **Main application (Menu):** python3 black_ops.py
 2. **Profile/Batch CLI:** python3 black_ops.py <subcommand> ...
 3. **Interactive Shell:** python3 black_ops_cli.py
### Global CLI Entry (black_ops.py)
```bash
python3 black_ops.py --help

```
**Important profiles:**
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
### Interactive Shell (black_ops_cli.py)
**Start:**
```bash
python3 black_ops_cli.py

```
**Important commands:**
 * show tools - lists all Python tool modules under tools/
 * show plugins - lists all loaded plugins incl. status
 * use <tool-path> - selects a tool (Example: use tools/recon/netscout.py)
 * set KEY VALUE - sets tool options (only if tool expects main(options))
 * run [--dry-run] - starts the active tool
 * plugin run <name> KEY=VALUE ... [--dry-run] - starts a plugin
 * back - resets the tool context
 * exit - closes the shell
**Examples:**
```bash
show tools
show plugins
plugin run sys_info
plugin run dns_lookup host=example.com
plugin run file_hash path=README.md algo=sha256

```
## Tool Catalog
> **Note:** Not every module is wired directly into the main menu. However, all modules can be started directly via Python (or in many cases via scan --tool ...).
> 
### Recon Tools
**1) tools.recon.social_hunter_v7**
 * **Purpose:** Username and email OSINT (incl. optional API-based leak checks)
 * **Execution:**
   * **Menu:** Recon -> Social Hunter v7
   * **CLI Profile:** python3 black_ops.py scan --tool tools.recon.social_hunter_v7
   * **Direct:**
     * python3 tools/recon/social_hunter_v7.py <target> -t username -o report.txt
     * python3 tools/recon/social_hunter_v7.py user@example.com -t email
 * **Parameters (direct):**
   * target: Username or Email
   * -t/--type: username | email
   * -o/--output: optional report path
 * **API Keys (optional for breach checks):** haveibeenpwned, dehashed (Possible in secrets.json via api_keys.haveibeenpwned / api_keys.dehashed)
**2) tools.recon.netscout_pro**
 * **Purpose:** Header analysis, subdomain bruteforce, fast port scan, JSON export
 * **Execution:**
   * **Menu:** Recon -> NetScout Pro
   * **CLI Profile:** python3 black_ops.py scan --tool tools.recon.netscout_pro
   * **Direct:** python3 tools/recon/netscout_pro.py example.com -t 30 -o netscout_pro.json
 * **Parameters:**
   * target: Domain/Host
   * -t/--threads: Thread count
   * -o/--output: JSON file
**3) tools.recon.metaspy**
 * **Purpose:** EXIF and GPS analysis of images
 * **Execution:**
   * **Menu:** Recon -> MetaSpy
   * **CLI Profile:** python3 black_ops.py scan --tool tools.recon.metaspy
   * **Direct interactive:** python3 tools/recon/metaspy.py
 * **Workflow:** Enter image path -> Metadata/GPS will be output -> Optional Maps link if coordinates are present.
**4) tools.recon.netscout (direct)**
 * **Purpose:** Basic Recon: HTTP headers, DNS records, optional port check
 * **Execution:**
   * python3 tools/recon/netscout.py example.com --scan-ports
   * python3 tools/recon/netscout.py example.com -v
**5) tools.recon.shodan_search (direct)**
 * **Purpose:** Shodan search (requires Shodan key)
 * **Execution:** python3 tools/recon/shodan_search.py "apache country:DE"
 * **Requirement:** shodan Python package, API key in secrets.json/Environment.
### Offensive Tools
**1) tools.offensive.airstrike**
 * **Purpose:** Port scan, ARP test, Load/DoS test in authorized test environments
 * **Execution:**
   * **Menu:** Offensive -> AirStrike
   * **CLI Profile:** python3 black_ops.py scan --tool tools.offensive.airstrike
   * **Direct:**
     * python3 tools/offensive/airstrike.py scan 192.168.1.10 -p 1-1024 -t tcp
     * python3 tools/offensive/airstrike.py arp 192.168.1.20 192.168.1.1 -i eth0
     * python3 tools/offensive/airstrike.py dos 192.168.1.10 80 -t http
**2) tools.offensive.netshark**
 * **Purpose:** ARP manipulation/MITM test with recovery logic
 * **Execution:**
   * **Menu:** Offensive -> NetShark
   * **CLI Profile:** python3 black_ops.py scan --tool tools.offensive.netshark
   * **Direct (root required):** sudo python3 tools/offensive/netshark.py
**3) tools.offensive.silent_phish**
 * **Purpose:** Simulated credential capture webflow for awareness/lab tests
 * **Execution:**
   * **Menu:** Offensive -> Silent Phish
   * **CLI Profile:** python3 black_ops.py scan --tool tools.offensive.silent_phish
   * **Direct:** python3 tools/offensive/silent_phish.py
 * **Workflow:** Optionally start tunnel -> Start local server -> Inputs are saved in loot.txt.
**4) tools.offensive.venom_maker**
 * **Purpose:** Payload generator with multiple templates and obfuscation levels
 * **Execution:**
   * **Menu:** Offensive -> Venom Maker
   * **CLI Profile:** python3 black_ops.py scan --tool tools.offensive.venom_maker
   * **Direct:** python3 tools/offensive/venom_maker.py
 * **Workflow:** Ethics confirmation -> Choose payload type -> Configure platform/obfuscation/options -> File is generated.
**5) tools.offensive.hashbreaker**
 * **Purpose:** Offline Dictionary Hash Cracking (md5/sha1/sha256)
 * **Execution:**
   * **Menu:** Offensive -> HashBreaker
   * **CLI Profile:** python3 black_ops.py scan --tool tools.offensive.hashbreaker
   * **Direct:** python3 tools/offensive/hashbreaker.py
 * **Inputs:** Algorithm, Target hash, Wordlist path (Default rockyou).
**6) tools.offensive.exploit_launcher (direct)**
 * **Purpose:** Search/download ExploitDB entries via searchsploit
 * **Execution:**
   * python3 tools/offensive/exploit_launcher.py search openssl
   * python3 tools/offensive/exploit_launcher.py run <EDB-ID> <TARGET_IP>
 * **Requirement:** searchsploit installed.
### Stealth Tools
**1) tools.stealth.ghost_net**
 * **Purpose:** Stealth HTTP requests, IP check, Proxy/Tor usage
 * **Execution:**
   * **Menu:** Stealth -> Ghost Net
   * **CLI Profile:** python3 black_ops.py scan --tool tools.stealth.ghost_net
   * **Direct:**
     * python3 tools/stealth/ghost_net.py ip
     * python3 tools/stealth/ghost_net.py ip --tor
     * python3 tools/stealth/ghost_net.py proxy -f data/configs/proxies.txt
     * python3 tools/stealth/ghost_net.py request https://example.com -m GET -d 1.5 --tor
**2) tools.stealth.traceless**
 * **Purpose:** Log/history cleaning functions (only in controlled test systems)
 * **Execution:**
   * **Menu:** Stealth -> Traceless
   * **CLI Profile:** python3 black_ops.py scan --tool tools.stealth.traceless
   * **Direct (root required):** sudo python3 tools/stealth/traceless.py
### Intelligence Tools
**1) tools.intelligence.neurolink**
 * **Purpose:** AI Advisor via OpenAI API
 * **Execution:**
   * **Menu:** Intelligence -> NeuroLink
   * **CLI Profile:** python3 black_ops.py scan --tool tools.intelligence.neurolink
   * **Direct:** python3 tools/intelligence/neurolink.py
 * **Requirement:** openai package, valid openai_key in secrets.json.
### Utility Tools
**1) tools.utils.cryptovault**
 * **Purpose:** Base64 Encode/Decode, Hashing, ROT13
 * **Execution:** Menu -> Utility -> CryptoVault / Direct: python3 tools/utils/cryptovault.py
**2) tools.utils.file_analyzer**
 * **Purpose:** File MIME, size, executable check, SHA256
 * **Execution:** Menu -> Utility -> File Analyzer / Direct: python3 tools/utils/file_analyzer.py
**3) tools.utils.network_scanner**
 * **Purpose:** Fast multiport TCP check
 * **Execution:** Menu -> Utility -> Network Scanner / Direct: python3 tools/utils/network_scanner.py
**4) tools.utils.system_info**
 * **Purpose:** Basic system info (OS, Hostname, IP, User)
 * **Execution:** Menu -> Utility -> System Info / Direct: python3 tools/utils/system_info.py
**5) tools.utils.evasion (Library)**
 * **Purpose:** Helper functions for obfuscation/mutation
 * **Usage as import:**
   ```python
   from tools.utils.evasion import Evasion
   
   payload = "print('hello')"
   enc = Evasion.base64_obfuscate(payload)
   
   ```
### Wireless Tools (currently not wired in the main menu)
**1) tools.wireless.wifi_scanner**
 * python3 tools/wireless/wifi_scanner.py
 * Uses airodump-ng, writes temporarily to /tmp/airodump-01.csv.
**2) tools.wireless.bluetooth_scanner**
 * python3 tools/wireless/bluetooth_scanner.py
 * Uses hcitool scan.
**3) tools.wireless.handshake_capture**
 * python3 tools/wireless/handshake_capture.py <interface> <bssid> <channel>
 * Activates monitor mode, captures for a defined timeout.
**4) tools.wireless.deauth_attack**
 * python3 tools/wireless/deauth_attack.py <BSSID> [interface]
 * Starts aireplay-ng with deauth frames.
## Plugin System
**Plugin path:** tools/plugins/<plugin_name>/plugin.py or tools/plugins/<plugin_name>.py
**Interactive Shell:**
```bash
python3 black_ops_cli.py
show plugins
plugin run <plugin_name> KEY=VALUE ...

```
### Available Plugins
**1) example_plugin**
 * plugin run ExamplePlugin
 * plugin run ExamplePlugin foo=bar
**2) sys_info**
 * **Purpose:** Runtime/system info
 * plugin run sys_info
 * plugin run sys_info env_keys=HOME,USER,SHELL
 * **Parameters:** env_keys (CSV list of environment variables)
**3) dns_lookup**
 * **Purpose:** DNS resolution of hostnames
 * plugin run dns_lookup host=example.com
 * **Parameters:** host (required)
**4) file_hash**
 * **Purpose:** File hashing
 * plugin run file_hash path=README.md
 * plugin run file_hash path=README.md algo=sha512
 * **Parameters:** path (required), algo (optional: sha256 (default), sha512, sha1, md5)
**5) secrets_leak_check**
 * **Purpose:** Source/text scan for potential secret leaks
 * **Examples:**
   * plugin run secrets_leak_check path=. include=*.py,*.env,*.json
   * plugin run secrets_leak_check path=. exclude=venv,.git,reports
   * plugin run secrets_leak_check path=. rules=strict workers=4 respect_gitignore=true
   * plugin run secrets_leak_check path=. baseline=.blackops/secrets-baseline.json write_baseline=true
   * plugin run secrets_leak_check path=. rules_file=custom_rules.json
 * **Important Parameters:**
   * path: Scan root (default .)
   * include: CSV glob list
   * exclude: CSV path parts
   * max_files: default 2000
   * max_file_size_kb: default 256
   * workers: default 1
   * respect_gitignore: true | false
   * rules: default | strict
   * rules_file: JSON rule file
   * baseline: Path to fingerprint baseline
   * write_baseline: true | false
   * fail_on_findings: true | false
   * exit_code: default 2
 * **custom_rules.json Example:**
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
**6) osint_domain_profile**
 * **Purpose:** Domain OSINT profile (DNS, TLS, HTTP headers, title)
 * plugin run osint_domain_profile domain=example.com
 * plugin run osint_domain_profile domain=example.com timeout=8
 * **Parameters:** domain (required), timeout (optional, seconds)
**7) osint_username_probe**
 * **Purpose:** Username existence check across multiple platforms
 * plugin run osint_username_probe username=octocat
 * plugin run osint_username_probe username=octocat sites=github,reddit,gitlab timeout=8
 * **Parameters:** username (required), sites (CSV selection, default: all known), timeout (optional)
 * **Known sites:** github, gitlab, reddit, medium, devto, pinterest
**8) osint_email_footprint**
 * **Purpose:** Basic profile for email (domain resolution + Gravatar hash)
 * plugin run osint_email_footprint email=user@example.com
 * **Parameters:** email (required)
## Troubleshooting
**Missing dependencies**
```bash
./install.sh
# or specifically
pip install -r requirements.txt

```
**Tool doesn't start from menu**
 * Check module path
 * Check Python dependencies of the module
 * Use --dry-run to validate execution
**Plugin not found**
 * Is the file located under tools/plugins/...?
 * Is there a class extending PluginInterface?
 * Check with show plugins
**Permission issues**
 * Some modules require root (e.g., Network/Wireless)
## Tests
```bash
python -m unittest discover -s tests

```
**Only unit tests:**
```bash
python -m unittest discover -s tests/unit_tests -v

```
## Sensitive Files
**Do not commit with real secrets:**
 * secrets.json
 * .env
 * blackops_config.json
**Report/Log outputs:**
 * logs/
 * reports/
