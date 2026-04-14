"""
Social Hunter v7 - Advanced OSINT & Reconnaissance Tool
"""

import requests
import json
import re
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None
import concurrent.futures

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.blackops_logger import BlackOpsLogger
from core.ethics_enforcer import EthicsEnforcer
from core.secrets_manager import SecretsManager

class SocialHunterV7:
    CONFIG_PATH = Path("data/configs/social_sites.json")
    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    SEARCH_TYPE_ALIASES = {
        "username": "username",
        "user": "username",
        "nick": "username",
        "nickname": "username",
        "u": "username",
        "email": "email",
        "mail": "email",
        "e-mail": "email",
        "emal": "email",  # tolerant alias for common typo
        "e": "email",
    }

    def __init__(self):
        self.logger = BlackOpsLogger("SocialHunterV7")
        self.ethics = EthicsEnforcer()
        self.secrets = SecretsManager()
        self.config = self._load_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def _load_config(self) -> Dict:
        """Lädt Konfiguration"""
        try:
            with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
        except Exception:
            loaded = {}
        return self._ensure_config_shape(loaded)

    def _ensure_config_shape(self, config: Dict) -> Dict:
        merged = dict(config or {})
        merged.setdefault("social_media", {})
        merged.setdefault("search_engines", {})
        merged.setdefault("data_breach_sites", {})
        for site_name, site_info in list(merged["social_media"].items()):
            if not isinstance(site_info, dict):
                merged["social_media"].pop(site_name, None)
                continue
            site_info.setdefault("enabled", True)
            if "url" in site_info and isinstance(site_info["url"], str):
                site_info["url"] = site_info["url"].strip()
        return merged

    def _save_config(self) -> None:
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as handle:
            json.dump(self.config, handle, indent=2, ensure_ascii=False)

    def _get_social_sites(self, enabled_only: bool = False) -> Dict[str, Dict]:
        sites = self.config.get("social_media", {})
        if not enabled_only:
            return sites
        return {
            name: info for name, info in sites.items()
            if isinstance(info, dict) and info.get("enabled", True)
        }

    def list_social_sites(self) -> Dict[str, Dict]:
        return self._get_social_sites(enabled_only=False)

    def add_social_site(self, site_name: str, url_template: str, enabled: bool = True) -> bool:
        normalized_name = (site_name or "").strip().lower()
        normalized_url = (url_template or "").strip()
        if not normalized_name or not normalized_url:
            return False
        if "{}" not in normalized_url:
            return False
        if not normalized_url.startswith(("http://", "https://")):
            return False

        social_media = self.config.setdefault("social_media", {})
        social_media[normalized_name] = {
            "url": normalized_url,
            "patterns": [],
            "enabled": bool(enabled),
        }
        self._save_config()
        return True

    def remove_social_site(self, site_name: str) -> bool:
        normalized_name = (site_name or "").strip().lower()
        if not normalized_name:
            return False
        social_media = self.config.setdefault("social_media", {})
        if normalized_name not in social_media:
            return False
        social_media.pop(normalized_name, None)
        self._save_config()
        return True

    def set_site_enabled(self, site_name: str, enabled: bool) -> bool:
        normalized_name = (site_name or "").strip().lower()
        site = self.config.setdefault("social_media", {}).get(normalized_name)
        if not isinstance(site, dict):
            return False
        site["enabled"] = bool(enabled)
        self._save_config()
        return True

    @classmethod
    def _looks_like_email(cls, target: str) -> bool:
        return bool(cls.EMAIL_RE.match((target or "").strip()))

    @classmethod
    def normalize_search_type(cls, search_type: str, target: str) -> str:
        normalized = cls.SEARCH_TYPE_ALIASES.get((search_type or "").strip().lower())
        if normalized:
            return normalized
        return "email" if cls._looks_like_email(target) else "username"
    
    def search_username(self, username: str) -> Dict[str, List[Dict]]:
        """Sucht Username auf sozialen Medien"""
        if not self.ethics.check_target(username):
            self.logger.error(f"Target not authorized: {username}")
            return {}
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_site = {}

            for site_name, site_info in self._get_social_sites(enabled_only=True).items():
                future = executor.submit(
                    self._check_site,
                    username,
                    site_name,
                    site_info
                )
                future_to_site[future] = site_name
            
            for future in concurrent.futures.as_completed(future_to_site):
                site_name = future_to_site[future]
                try:
                    result = future.result()
                    if result:
                        results[site_name] = result
                except Exception as e:
                    self.logger.error(f"Error checking {site_name}: {e}")
        
        return results
    
    def _check_site(self, username: str, site_name: str, site_info: Dict) -> Optional[Dict]:
        """Prüft Username auf einer bestimmten Seite"""
        try:
            url = site_info['url'].format(username)
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser') if BeautifulSoup else None
                page_text = soup.get_text(separator=" ", strip=True) if soup else response.text
                
                # Different checks for different sites
                if site_name == 'github':
                    # Check for GitHub specific indicators
                    if 'Page not found' not in page_text and \
                       'Not Found' not in page_text:
                        return {
                            'url': url,
                            'status': 'found',
                            'data': self._extract_github_data(soup)
                        }
                
                elif site_name == 'twitter':
                    # Check for Twitter indicators
                    if 'This account doesn\'t exist' not in page_text:
                        return {
                            'url': url,
                            'status': 'found',
                            'data': self._extract_twitter_data(soup)
                        }
                
                # Generic check
                if len(page_text) > 1000:  # Likely a real page
                    return {
                        'url': url,
                        'status': 'found',
                        'data': self._extract_generic_data(soup, response.text)
                    }
            
            elif response.status_code == 404:
                return {
                    'url': url,
                    'status': 'not_found'
                }
            
        except Exception as e:
            self.logger.debug(f"Error checking {site_name}: {e}")
        
        return None
    
    def _extract_github_data(self, soup) -> Dict:
        """Extrahiert GitHub Daten"""
        if soup is None:
            return {}
        data = {}
        
        try:
            # Extract name
            name_elem = soup.find('span', {'itemprop': 'name'})
            if name_elem:
                data['name'] = name_elem.text.strip()
            
            # Extract bio
            bio_elem = soup.find('div', class_='p-note')
            if bio_elem:
                data['bio'] = bio_elem.text.strip()
            
            # Extract location
            location_elem = soup.find('span', class_='p-label')
            if location_elem:
                data['location'] = location_elem.text.strip()
            
            # Extract stats
            stats = {}
            stat_elements = soup.find_all('span', class_='text-bold')
            for elem in stat_elements:
                if 'repositories' in elem.parent.text.lower():
                    stats['repositories'] = elem.text.strip()
                elif 'followers' in elem.parent.text.lower():
                    stats['followers'] = elem.text.strip()
                elif 'following' in elem.parent.text.lower():
                    stats['following'] = elem.text.strip()
            
            data['stats'] = stats
            
        except Exception as e:
            self.logger.debug(f"Error extracting GitHub data: {e}")
        
        return data
    
    def _extract_twitter_data(self, soup) -> Dict:
        """Extrahiert Twitter Daten"""
        data = {}
        
        try:
            # Twitter has complex structure, use patterns
            text = soup.get_text() if soup is not None else ""
            
            # Extract name
            name_match = re.search(r'@[\w]+', text)
            if name_match:
                data['username'] = name_match.group()
            
            # Extract bio
            bio_patterns = ['bio', 'description', 'Bio', 'Description']
            for pattern in bio_patterns:
                if pattern in text:
                    # Simple extraction
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if pattern.lower() in line.lower():
                            if i + 1 < len(lines):
                                data['bio'] = lines[i + 1].strip()
                            break
            
        except Exception as e:
            self.logger.debug(f"Error extracting Twitter data: {e}")
        
        return data
    
    def _extract_generic_data(self, soup, raw_html: str = "") -> Dict:
        """Extrahiert generische Daten"""
        data = {}
        
        try:
            if soup is None:
                return data
            # Extract title
            title = soup.title.string if soup.title else None
            if title:
                data['title'] = title.strip()
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                data['description'] = meta_desc['content'].strip()
            
            # Extract images
            images = []
            for img in soup.find_all('img', src=True):
                if img['src'].startswith('http'):
                    images.append(img['src'])
            
            if images:
                data['images'] = images[:5]  # First 5 images
            
        except Exception as e:
            self.logger.debug(f"Error extracting generic data: {e}")
        
        return data
    
    def search_email(self, email: str) -> Dict:
        """Sucht Email in Datenlecks"""
        if not self.ethics.get_approval(email, "email_search", "Data breach checking"):
            return {}
        
        results = {}
        
        # Check Have I Been Pwned
        hibp_results = self._check_hibp(email)
        if hibp_results:
            results['haveibeenpwned'] = hibp_results
        
        # Check Dehashed
        dehashed_results = self._check_dehashed(email)
        if dehashed_results:
            results['dehashed'] = dehashed_results
        
        return results
    
    def _check_hibp(self, email: str) -> Optional[Dict]:
        """Prüft Have I Been Pwned"""
        try:
            # Note: Requires API key
            api_key = self._get_api_key('haveibeenpwned')
            if not api_key:
                return None
            
            headers = {
                'hibp-api-key': api_key,
                'User-Agent': 'BlackOps-Framework'
            }
            
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                breaches = response.json()
                return {
                    'breach_count': len(breaches),
                    'breaches': breaches[:5]  # First 5 breaches
                }
            elif response.status_code == 404:
                return {'breach_count': 0}
            
        except Exception as e:
            self.logger.debug(f"Error checking HIBP: {e}")
        
        return None
    
    def _check_dehashed(self, email: str) -> Optional[Dict]:
        """Prüft Dehashed"""
        try:
            # Note: Requires API key
            api_key = self._get_api_key('dehashed')
            if not api_key:
                return None
            
            headers = {
                'Authorization': f'Bearer {api_key}'
            }
            
            url = f"https://api.dehashed.com/search?query=email:{email}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('entries'):
                    return {
                        'entry_count': len(data['entries']),
                        'entries': data['entries'][:5]
                    }
            
        except Exception as e:
            self.logger.debug(f"Error checking Dehashed: {e}")
        
        return None
    
    def _get_api_key(self, service: str) -> Optional[str]:
        """Holt API Key"""
        return (
            self.secrets.get(f"api_keys.{service}")
            or self.secrets.get(service)
            or self.secrets.get(f"{service}_api_key")
        )
    
    def generate_report(self, username: str, results: Dict) -> str:
        """Generiert Report"""
        report = f"""
        Social Media Reconnaissance Report
        =================================
        
        Target: {username}
        Search Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
        
        """
        
        for site_name, site_data in results.items():
            report += f"\n{site_name.upper()}:\n"
            report += "-" * 40 + "\n"
            
            if isinstance(site_data, dict):
                for key, value in site_data.items():
                    report += f"  {key}: {value}\n"
            elif isinstance(site_data, list):
                for item in site_data:
                    report += f"  - {item}\n"
        
        return report

    def _print_sites(self) -> None:
        sites = self.list_social_sites()
        print("\nConfigured sites (Konfigurierte Seiten):")
        if not sites:
            print("  - none (keine)")
            return
        for name, info in sorted(sites.items()):
            status = "enabled" if info.get("enabled", True) else "disabled"
            print(f"  - {name}: {info.get('url', '-') } [{status}]")
    
    def _search_and_print(self, target: str, search_type: str, output: Optional[str] = None) -> None:
        resolved_type = self.normalize_search_type(search_type, target)
        self.logger.print_banner()
        print(f"Search type (Suchtyp): {resolved_type}")
        if resolved_type == 'username':
            results = self.search_username(target)
        else:
            results = self.search_email(target)
        report = self.generate_report(target, results)
        print(report)
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"Report saved to {output}")

    def run(self):
        """Hauptfunktion für CLI oder Menü"""
        import argparse
        import sys

        # Menü-Modus: keine CLI-Argumente vorhanden
        if len(sys.argv) <= 1:
            while True:
                self.logger.print_banner()
                print("\n1) Search target (Ziel suchen)")
                print("2) List sites (Seiten anzeigen)")
                print("3) Add site (Seite hinzufügen)")
                print("4) Remove site (Seite entfernen)")
                print("5) Enable site (Seite aktivieren)")
                print("6) Disable site (Seite deaktivieren)")
                print("0) Back (Zurück)")
                action = input("\nSelect action (Aktion wählen): ").strip()
                if action in {"0", ""}:
                    return
                if action == "2":
                    self._print_sites()
                    input("\nEnter to continue...")
                    continue
                if action == "3":
                    name = input("Site name (Seitenname): ").strip()
                    url = input("URL template with {} (URL-Vorlage mit {}): ").strip()
                    if self.add_social_site(name, url):
                        print("Site added.")
                    else:
                        print("Could not add site. Use http(s)://... with {}.")
                    input("\nEnter to continue...")
                    continue
                if action == "4":
                    name = input("Site name to remove (Seite entfernen): ").strip()
                    print("Removed." if self.remove_social_site(name) else "Site not found.")
                    input("\nEnter to continue...")
                    continue
                if action == "5":
                    name = input("Site name to enable (Seite aktivieren): ").strip()
                    print("Enabled." if self.set_site_enabled(name, True) else "Site not found.")
                    input("\nEnter to continue...")
                    continue
                if action == "6":
                    name = input("Site name to disable (Seite deaktivieren): ").strip()
                    print("Disabled." if self.set_site_enabled(name, False) else "Site not found.")
                    input("\nEnter to continue...")
                    continue
                if action != "1":
                    print("Invalid action.")
                    time.sleep(1)
                    continue
                target = input("Target (username/email, empty = back): ").strip()
                if not target:
                    continue
                search_type = input("Type (username/email/auto) [auto]: ").strip().lower() or "auto"
                output = input("Output file (optional): ").strip() or None
                self._search_and_print(target, search_type, output)
                input("\nEnter to continue...")
        else:
            parser = argparse.ArgumentParser(description="Social Hunter v7 - OSINT Tool")
            parser.add_argument("target", nargs="?", help="Username or email to search")
            parser.add_argument("-t", "--type", default="auto", help="Search type: username/email/auto")
            parser.add_argument("-o", "--output", help="Output file")
            parser.add_argument("--list-sites", action="store_true", help="List configured social sites")
            parser.add_argument("--add-site", nargs=2, metavar=("NAME", "URL_TEMPLATE"), help="Add social site (url must include {})")
            parser.add_argument("--remove-site", metavar="NAME", help="Remove social site")
            parser.add_argument("--enable-site", metavar="NAME", help="Enable social site")
            parser.add_argument("--disable-site", metavar="NAME", help="Disable social site")
            args = parser.parse_args()
            if args.list_sites:
                self._print_sites()
                return
            if args.add_site:
                name, url = args.add_site
                ok = self.add_social_site(name, url)
                print("Site added." if ok else "Could not add site. Use http(s)://... with {}.")
                return
            if args.remove_site:
                print("Removed." if self.remove_social_site(args.remove_site) else "Site not found.")
                return
            if args.enable_site:
                print("Enabled." if self.set_site_enabled(args.enable_site, True) else "Site not found.")
                return
            if args.disable_site:
                print("Disabled." if self.set_site_enabled(args.disable_site, False) else "Site not found.")
                return
            if not args.target:
                parser.error("target is required for search mode")
            self._search_and_print(args.target, args.type, args.output)

if __name__ == "__main__":
    SocialHunterV7().run()
