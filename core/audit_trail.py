"""
Audit Trail System für Black Ops Framework
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import hashlib

class AuditTrail:
    def __init__(self):
        self.audit_log = Path("logs/audit/audit_trail.json")
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
        self.entries = []
        self._load_audit_log()
    
    def _load_audit_log(self):
        """Lädt Audit-Log"""
        if self.audit_log.exists():
            with open(self.audit_log, 'r') as f:
                self.entries = json.load(f)
        else:
            self.entries = []
    
    def _save_audit_log(self):
        """Speichert Audit-Log"""
        with open(self.audit_log, 'w') as f:
            json.dump(self.entries, f, indent=2)
        
        # Create hash for integrity verification
        hash_file = self.audit_log.with_suffix('.hash')
        with open(self.audit_log, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        with open(hash_file, 'w') as f:
            f.write(file_hash)
    
    def log_event(self, user: str, action: str, target: str, 
                  details: Dict = None, status: str = "SUCCESS") -> str:
        """Loggt ein Event"""
        event_id = hashlib.sha256(
            f"{user}_{action}_{target}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        event = {
            'id': event_id,
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'action': action,
            'target': target,
            'details': details or {},
            'status': status,
            'checksum': self._calculate_event_checksum(user, action, target, details)
        }
        
        self.entries.append(event)
        
        # Keep only last 10000 entries
        if len(self.entries) > 10000:
            self.entries = self.entries[-5000:]
        
        self._save_audit_log()
        return event_id
    
    def _calculate_event_checksum(self, user: str, action: str, 
                                 target: str, details: Dict) -> str:
        """Berechnet Checksum für Event"""
        data_string = f"{user}:{action}:{target}:{json.dumps(details, sort_keys=True)}"
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def verify_integrity(self) -> Dict:
        """Verifiziert Integrität des Audit-Logs"""
        results = {
            'total_entries': len(self.entries),
            'corrupted_entries': 0,
            'missing_checksums': 0,
            'integrity_verified': True
        }
        
        for entry in self.entries:
            # Check if checksum exists
            if 'checksum' not in entry:
                results['missing_checksums'] += 1
                results['integrity_verified'] = False
                continue
            
            # Recalculate checksum
            expected_checksum = self._calculate_event_checksum(
                entry['user'],
                entry['action'],
                entry['target'],
                entry.get('details', {})
            )
            
            if entry['checksum'] != expected_checksum:
                results['corrupted_entries'] += 1
                results['integrity_verified'] = False
        
        return results
    
    def search_events(self, user: Optional[str] = None, 
                     action: Optional[str] = None,
                     target: Optional[str] = None,
                     status: Optional[str] = None,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None) -> List[Dict]:
        """Sucht Events nach Kriterien"""
        results = []
        
        for entry in self.entries:
            # Apply filters
            if user and entry['user'] != user:
                continue
            if action and entry['action'] != action:
                continue
            if target and entry['target'] != target:
                continue
            if status and entry['status'] != status:
                continue
            
            # Date filter
            entry_date = datetime.fromisoformat(entry['timestamp'])
            
            if start_date:
                start = datetime.fromisoformat(start_date)
                if entry_date < start:
                    continue
            
            if end_date:
                end = datetime.fromisoformat(end_date)
                if entry_date > end:
                    continue
            
            results.append(entry)
        
        return results
    
    def generate_report(self, period: str = "daily") -> Dict:
        """Generiert Audit-Report"""
        now = datetime.now()
        
        if period == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            start_date = now.replace(day=now.day - 7)
        elif period == "monthly":
            start_date = now.replace(month=now.month - 1)
        else:
            start_date = now.replace(year=now.year - 1)  # yearly
        
        # Filter entries for period
        period_entries = []
        for entry in self.entries:
            entry_date = datetime.fromisoformat(entry['timestamp'])
            if entry_date >= start_date:
                period_entries.append(entry)
        
        # Generate statistics
        stats = {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': now.isoformat(),
            'total_events': len(period_entries),
            'events_by_user': {},
            'events_by_action': {},
            'events_by_status': {},
            'top_targets': {}
        }
        
        for entry in period_entries:
            # Count by user
            stats['events_by_user'][entry['user']] = \
                stats['events_by_user'].get(entry['user'], 0) + 1
            
            # Count by action
            stats['events_by_action'][entry['action']] = \
                stats['events_by_action'].get(entry['action'], 0) + 1
            
            # Count by status
            stats['events_by_status'][entry['status']] = \
                stats['events_by_status'].get(entry['status'], 0) + 1
            
            # Count by target
            stats['top_targets'][entry['target']] = \
                stats['top_targets'].get(entry['target'], 0) + 1
        
        # Sort top targets
        stats['top_targets'] = dict(
            sorted(stats['top_targets'].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return stats
    
    def export_audit_log(self, format: str = "json") -> str:
        """Exportiert Audit-Log"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = Path("reports/exports/audit")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            filename = f"audit_log_{timestamp}.json"
            filepath = export_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(self.entries, f, indent=2)
        
        elif format == "csv":
            filename = f"audit_log_{timestamp}.csv"
            filepath = export_dir / filename
            
            import csv
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Timestamp', 'User', 'Action', 
                                'Target', 'Status', 'Details'])
                
                for entry in self.entries:
                    writer.writerow([
                        entry['id'],
                        entry['timestamp'],
                        entry['user'],
                        entry['action'],
                        entry['target'],
                        entry['status'],
                        json.dumps(entry.get('details', {}))
                    ])
        
        elif format == "html":
            filename = f"audit_log_{timestamp}.html"
            filepath = export_dir / filename
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Audit Log Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #4CAF50; color: white; }
                    tr:nth-child(even) { background-color: #f2f2f2; }
                    .success { color: green; }
                    .failure { color: red; }
                </style>
            </head>
            <body>
                <h1>Audit Log Report</h1>
                <p>Generated: """ + datetime.now().isoformat() + """</p>
                <p>Total Entries: """ + str(len(self.entries)) + """</p>
                <table>
                    <tr>
                        <th>Timestamp</th>
                        <th>User</th>
                        <th>Action</th>
                        <th>Target</th>
                        <th>Status</th>
                        <th>Details</th>
                    </tr>
            """
            
            for entry in self.entries[-1000:]:  # Last 1000 entries
                status_class = "success" if entry['status'] == "SUCCESS" else "failure"
                html_content += f"""
                    <tr>
                        <td>{entry['timestamp']}</td>
                        <td>{entry['user']}</td>
                        <td>{entry['action']}</td>
                        <td>{entry['target']}</td>
                        <td class="{status_class}">{entry['status']}</td>
                        <td>{json.dumps(entry.get('details', {}))}</td>
                    </tr>
                """
            
            html_content += """
                </table>
                <p>Report generated by Black Ops Framework v2.2</p>
            </body>
            </html>
            """
            
            with open(filepath, 'w') as f:
                f.write(html_content)
        
        return str(filepath)