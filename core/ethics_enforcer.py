"""
Ethics Enforcement System für Black Ops Framework
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class EthicsEnforcer:
    def __init__(self, config_path: str = "data/configs/ethics_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.violations = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Lädt Ethics-Konfiguration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Default Ethics Configuration
        return {
            "rules": {
                "no_illegal_activities": True,
                "authorized_targets_only": True,
                "data_protection": True,
                "compliance_with_laws": True,
                "responsible_disclosure": True
            },
            "restrictions": {
                "forbidden_targets": [
                    "*.gov",
                    "*.mil",
                    "critical_infrastructure",
                    "healthcare_systems"
                ],
                "allowed_actions": [
                    "penetration_testing",
                    "vulnerability_scanning",
                    "security_research"
                ],
                "forbidden_actions": [
                    "data_destruction",
                    "ransomware",
                    "service_disruption",
                    "identity_theft"
                ]
            },
            "approval_required": True,
            "logging_level": "DETAILED"
        }
    
    def check_target(self, target: str) -> bool:
        """Prüft ob Target erlaubt ist"""
        # Domain Validation
        forbidden_patterns = self.config["restrictions"]["forbidden_targets"]
        
        for pattern in forbidden_patterns:
            if pattern.startswith("*."):
                domain_suffix = pattern[2:]
                if target.endswith(domain_suffix):
                    self._log_violation(f"Forbidden target pattern matched: {target}")
                    return False
        
        # Blacklist Check
        blacklist = self._load_blacklist()
        target_hash = hashlib.sha256(target.encode()).hexdigest()
        
        if target_hash in blacklist:
            self._log_violation(f"Target in blacklist: {target}")
            return False
        
        return True
    
    def check_action(self, action: str) -> bool:
        """Prüft ob Aktion erlaubt ist"""
        forbidden_actions = self.config["restrictions"]["forbidden_actions"]
        
        if action in forbidden_actions:
            self._log_violation(f"Forbidden action: {action}")
            return False
        
        return True
    
    def get_approval(self, target: str, action: str, reason: str) -> bool:
        """Holt Genehmigung für Aktion"""
        if not self.config["approval_required"]:
            return True
        
        print(f"\n[ETHICS APPROVAL REQUIRED]")
        print(f"Target: {target}")
        print(f"Action: {action}")
        print(f"Reason: {reason}")
        print(f"\nAre you authorized to perform this action? (yes/NO): ")
        
        response = input().strip().lower()
        if response == "yes":
            self._log_approval(target, action, reason)
            return True
        
        self._log_violation(f"Approval denied for: {target} - {action}")
        return False
    
    def _load_blacklist(self) -> List[str]:
        """Lädt Blacklist"""
        blacklist_path = Path("data/configs/blacklist.json")
        if blacklist_path.exists():
            with open(blacklist_path, 'r') as f:
                return json.load(f)
        return []
    
    def _log_violation(self, message: str) -> None:
        """Loggt Ethics-Verletzung"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "violation": message,
            "action": "BLOCKED"
        }
        self.violations.append(violation)
        
        # Save to file
        violations_path = Path("logs/audit/ethics_violations.json")
        violations_path.parent.mkdir(parents=True, exist_ok=True)
        
        existing = []
        if violations_path.exists():
            with open(violations_path, 'r') as f:
                existing = json.load(f)
        
        existing.append(violation)
        
        with open(violations_path, 'w') as f:
            json.dump(existing, f, indent=2)
    
    def _log_approval(self, target: str, action: str, reason: str) -> None:
        """Loggt Genehmigung"""
        approval = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "action": action,
            "reason": reason,
            "status": "APPROVED"
        }
        
        approvals_path = Path("logs/audit/ethics_approvals.json")
        approvals_path.parent.mkdir(parents=True, exist_ok=True)
        
        existing = []
        if approvals_path.exists():
            with open(approvals_path, 'r') as f:
                existing = json.load(f)
        
        existing.append(approval)
        
        with open(approvals_path, 'w') as f:
            json.dump(existing, f, indent=2)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generiert Ethics-Report"""
        return {
            "total_checks": len(self.violations) + self._count_approvals(),
            "violations": len(self.violations),
            "approvals": self._count_approvals(),
            "violation_details": self.violations,
            "compliance_status": "COMPLIANT" if len(self.violations) == 0 else "NON_COMPLIANT"
        }
    
    def _count_approvals(self) -> int:
        """Zählt Genehmigungen"""
        approvals_path = Path("logs/audit/ethics_approvals.json")
        if approvals_path.exists():
            with open(approvals_path, 'r') as f:
                approvals = json.load(f)
                return len(approvals)
        return 0