"""
Social Hunter v7 - Advanced OSINT & Reconnaissance Tool
"""

import requests
import json
import re
import time
from typing import Dict, List, Optional, Set
from bs4 import BeautifulSoup
import concurrent.futures
from core.blackops_logger import BlackOpsLogger
from core.ethics_enforcer import EthicsEnforcer
from core.secrets_manager import SecretsManager

class SocialHunterV7:
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
            with open('data/configs/social_sites.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def search_username(self, username: str) -> Dict[str, List[Dict]]:
        """Sucht Username auf sozialen Medien"""
        if not self.ethics.check_target(username):
            self.logger.error(f"Target not authorized: {username}")
            return {}
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_site = {}
            
            for site_name, site_info in self.config.get('social_media', {}).items():
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
                # Check for specific patterns
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Different checks for different sites
                if site_name == 'github':
                    # Check for GitHub specific indicators
                    if 'Page not found' not in soup.text and \
                       'Not Found' not in soup.text:
                        return {
                            'url': url,
                            'status': 'found',
                            'data': self._extract_github_data(soup)
                        }
                
                elif site_name == 'twitter':
                    # Check for Twitter indicators
                    if 'This account doesn\'t exist' not in soup.text:
                        return {
                            'url': url,
                            'status': 'found',
                            'data': self._extract_twitter_data(soup)
                        }
                
                # Generic check
                if len(soup.text) > 1000:  # Likely a real page
                    return {
                        'url': url,
                        'status': 'found',
                        'data': self._extract_generic_data(soup)
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
            text = soup.get_text()
            
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
    
    def _extract_generic_data(self, soup) -> Dict:
        """Extrahiert generische Daten"""
        data = {}
        
        try:
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
    
    def run(self):
        """Hauptfunktion für CLI oder Menü"""
        import argparse
        import sys

        # Menü-Modus: keine CLI-Argumente vorhanden
        if len(sys.argv) <= 1:
            self.logger.print_banner()
            target = input("Target (username/email, leer = zurück): ").strip()
            if not target:
                return
            search_type = input("Type (username/email) [username]: ").strip().lower() or "username"
            if search_type not in ("username", "email"):
                print("Invalid type.")
                return
            output = input("Output file (optional): ").strip() or None
        else:
            parser = argparse.ArgumentParser(description="Social Hunter v7 - OSINT Tool")
            parser.add_argument("target", help="Username or email to search")
            parser.add_argument("-t", "--type", choices=['username', 'email'], 
                              default='username', help="Search type")
            parser.add_argument("-o", "--output", help="Output file")
            args = parser.parse_args()
            target = args.target
            search_type = args.type
            output = args.output
        
        self.logger.print_banner()
        
        if search_type == 'username':
            results = self.search_username(target)
        else:
            results = self.search_email(target)
        
        report = self.generate_report(target, results)
        
        print(report)
        
        if output:
            with open(output, 'w') as f:
                f.write(report)
            self.logger.info(f"Report saved to {output}")

if __name__ == "__main__":
    SocialHunterV7().run()
