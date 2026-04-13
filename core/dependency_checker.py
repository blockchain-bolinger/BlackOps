"""
Dependency Checker für Black Ops Framework
"""

import importlib
from importlib import metadata as importlib_metadata
from typing import Dict, List, Tuple

try:
    import pkg_resources
except ImportError:
    pkg_resources = None

class DependencyChecker:
    def __init__(self):
        self.required_packages = {
            'core': [
                ('requests', '2.28.0'),
                ('colorama', '0.4.6'),
                ('cryptography', '38.0.0'),
                ('pyyaml', '6.0')
            ],
            'network': [
                ('scapy', '2.5.0'),
                ('dnspython', '2.3.0'),
                ('netifaces', '0.11.0')
            ],
            'web': [
                ('beautifulsoup4', '4.11.0'),
                ('selenium', '4.8.0'),
                ('lxml', '4.9.0')
            ],
            'data': [
                ('pandas', '1.5.0'),
                ('numpy', '1.23.0')
            ],
            'reporting': [
                ('reportlab', '3.6.0')
            ],
            'optional': [
                ('geoip2', '4.6.0'),
                ('whois', '0.9.0'),
                ('paramiko', '3.0.0')
            ]
        }
    
    def check_all_dependencies(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Prüft alle Abhängigkeiten"""
        results = {
            'missing': [],
            'outdated': [],
            'satisfied': [],
            'errors': []
        }
        
        for category, packages in self.required_packages.items():
            for package, required_version in packages:
                try:
                    installed_version = self._get_package_version(package)
                    
                    if not installed_version:
                        results['missing'].append((package, required_version, category))
                    elif self._version_compare(installed_version, required_version) < 0:
                        results['outdated'].append(
                            (package, required_version, installed_version, category)
                        )
                    else:
                        results['satisfied'].append(
                            (package, required_version, installed_version, category)
                        )
                        
                except Exception as e:
                    results['errors'].append((package, str(e)))
        
        return results
    
    def _get_package_version(self, package_name: str) -> str:
        """Holt installierte Version"""
        if pkg_resources is not None:
            try:
                return pkg_resources.get_distribution(package_name).version
            except pkg_resources.DistributionNotFound:
                pass
            except Exception:
                pass

        try:
            return importlib_metadata.version(package_name)
        except importlib_metadata.PackageNotFoundError:
            pass
        except Exception:
            pass

        try:
            module = importlib.import_module(package_name)
            if hasattr(module, '__version__'):
                return module.__version__
            if hasattr(module, 'VERSION'):
                return str(module.VERSION)
        except Exception:
            pass

        return None
    
    def _version_compare(self, v1: str, v2: str) -> int:
        """Vergleicht Versionen"""
        from packaging import version
        
        try:
            v1_parsed = version.parse(v1)
            v2_parsed = version.parse(v2)
            
            if v1_parsed < v2_parsed:
                return -1
            elif v1_parsed > v2_parsed:
                return 1
            else:
                return 0
        except:
            # Fallback simple comparison
            return 0
    
    def generate_install_commands(self, results: Dict) -> List[str]:
        """Generiert Installationsbefehle"""
        commands = []
        
        # Install missing packages
        if results['missing']:
            missing_packages = [p[0] for p in results['missing']]
            commands.append(f"pip install {' '.join(missing_packages)}")
        
        # Upgrade outdated packages
        if results['outdated']:
            outdated_packages = [p[0] for p in results['outdated']]
            commands.append(f"pip install --upgrade {' '.join(outdated_packages)}")
        
        # Optional packages
        optional_packages = [p[0] for p in self.required_packages['optional']]
        commands.append(f"# Optional: pip install {' '.join(optional_packages)}")
        
        return commands
    
    def print_report(self, results: Dict):
        """Druckt Dependency Report"""
        print("\n" + "="*60)
        print("DEPENDENCY CHECK REPORT")
        print("="*60)
        
        # Satisfied
        if results['satisfied']:
            print("\n✓ SATISFIED DEPENDENCIES:")
            for package, required, installed, category in results['satisfied']:
                print(f"  {package}: {installed} (required: {required}) [{category}]")
        
        # Outdated
        if results['outdated']:
            print("\n⚠ OUTDATED DEPENDENCIES:")
            for package, required, installed, category in results['outdated']:
                print(f"  {package}: {installed} → {required} [{category}]")
        
        # Missing
        if results['missing']:
            print("\n✗ MISSING DEPENDENCIES:")
            for package, required, category in results['missing']:
                print(f"  {package}: missing (required: {required}) [{category}]")
        
        # Errors
        if results['errors']:
            print("\n❌ ERRORS:")
            for package, error in results['errors']:
                print(f"  {package}: {error}")
        
        print("\n" + "="*60)
        
        # Installation commands
        if results['missing'] or results['outdated']:
            print("\nINSTALLATION COMMANDS:")
            commands = self.generate_install_commands(results)
            for cmd in commands:
                print(f"  {cmd}")
