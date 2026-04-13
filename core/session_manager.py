"""
Session Management System für Black Ops Framework
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.active_sessions = {}
        self.session_file = Path("data/sessions/sessions.json")
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_sessions()
        
    def _load_sessions(self):
        """Lädt gespeicherte Sessions"""
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                self.sessions = json.load(f)
    
    def _save_sessions(self):
        """Speichert Sessions"""
        with open(self.session_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def create_session(self, user: str, tool: str, target: str, 
                      description: str = "") -> str:
        """Erstellt eine neue Session"""
        session_id = hashlib.sha256(
            f"{user}_{tool}_{target}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        session = {
            'id': session_id,
            'user': user,
            'tool': tool,
            'target': target,
            'description': description,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'status': 'active',
            'data': {},
            'logs': [],
            'commands': []
        }
        
        self.sessions[session_id] = session
        self.active_sessions[session_id] = session
        
        # Create session directory
        session_dir = Path(f"logs/sessions/session_{session_id}")
        session_dir.mkdir(parents=True, exist_ok=True)
        
        self._save_sessions()
        return session_id
    
    def end_session(self, session_id: str, status: str = "completed") -> bool:
        """Beendet eine Session"""
        if session_id in self.sessions:
            self.sessions[session_id]['end_time'] = datetime.now().isoformat()
            self.sessions[session_id]['status'] = status
            
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            self._save_sessions()
            return True
        return False
    
    def add_log(self, session_id: str, log_type: str, message: str) -> bool:
        """Fügt Log zur Session hinzu"""
        if session_id in self.sessions:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': log_type,
                'message': message
            }
            
            self.sessions[session_id]['logs'].append(log_entry)
            
            # Save to session log file
            log_file = Path(f"logs/sessions/session_{session_id}/session.log")
            with open(log_file, 'a') as f:
                f.write(f"[{log_entry['timestamp']}] {log_type}: {message}\n")
            
            self._save_sessions()
            return True
        return False
    
    def add_command(self, session_id: str, command: str, output: str) -> bool:
        """Fügt Befehl zur Session hinzu"""
        if session_id in self.sessions:
            cmd_entry = {
                'timestamp': datetime.now().isoformat(),
                'command': command,
                'output': output
            }
            
            self.sessions[session_id]['commands'].append(cmd_entry)
            self._save_sessions()
            return True
        return False
    
    def update_data(self, session_id: str, key: str, value: Any) -> bool:
        """Aktualisiert Session-Daten"""
        if session_id in self.sessions:
            self.sessions[session_id]['data'][key] = value
            self._save_sessions()
            return True
        return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Holt Session-Informationen"""
        return self.sessions.get(session_id)
    
    def get_active_sessions(self) -> Dict[str, Dict]:
        """Holt alle aktiven Sessions"""
        return self.active_sessions
    
    def list_sessions(self, user: Optional[str] = None, 
                     tool: Optional[str] = None) -> List[Dict]:
        """Listet Sessions mit Filtern"""
        sessions_list = []
        
        for session_id, session in self.sessions.items():
            if user and session['user'] != user:
                continue
            if tool and session['tool'] != tool:
                continue
            
            sessions_list.append({
                'id': session_id,
                'user': session['user'],
                'tool': session['tool'],
                'target': session['target'],
                'start_time': session['start_time'],
                'status': session['status']
            })
        
        return sessions_list
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Bereinigt alte Sessions"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned = 0
        
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if session['end_time']:
                end_date = datetime.fromisoformat(session['end_time'])
                if end_date < cutoff_date:
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            # Remove session directory
            session_dir = Path(f"logs/sessions/session_{session_id}")
            if session_dir.exists():
                import shutil
                shutil.rmtree(session_dir)
            
            del self.sessions[session_id]
            cleaned += 1
        
        if cleaned > 0:
            self._save_sessions()
        
        return cleaned
    
    def generate_session_report(self, session_id: str) -> Dict:
        """Generiert Session-Report"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        # Calculate duration
        start_time = datetime.fromisoformat(session['start_time'])
        end_time = datetime.now()
        if session['end_time']:
            end_time = datetime.fromisoformat(session['end_time'])
        
        duration = end_time - start_time
        
        return {
            'session_id': session_id,
            'user': session['user'],
            'tool': session['tool'],
            'target': session['target'],
            'description': session['description'],
            'start_time': session['start_time'],
            'end_time': session['end_time'],
            'duration': str(duration),
            'status': session['status'],
            'log_count': len(session['logs']),
            'command_count': len(session['commands']),
            'data_points': len(session['data'])
        }
    
    def export_session(self, session_id: str, format: str = "json") -> str:
        """Exportiert Session"""
        session = self.get_session(session_id)
        if not session:
            return ""
        
        export_dir = Path("reports/exports/sessions")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{session_id}_{timestamp}.{format}"
        export_path = export_dir / filename
        
        if format == "json":
            with open(export_path, 'w') as f:
                json.dump(session, f, indent=2)
        elif format == "txt":
            with open(export_path, 'w') as f:
                f.write(f"Session ID: {session_id}\n")
                f.write(f"User: {session['user']}\n")
                f.write(f"Tool: {session['tool']}\n")
                f.write(f"Target: {session['target']}\n")
                f.write(f"Start: {session['start_time']}\n")
                f.write(f"End: {session['end_time'] or 'Active'}\n")
                f.write(f"Status: {session['status']}\n")
                f.write("\n--- Logs ---\n")
                for log in session['logs']:
                    f.write(f"[{log['timestamp']}] {log['type']}: {log['message']}\n")
                f.write("\n--- Commands ---\n")
                for cmd in session['commands']:
                    f.write(f"[{cmd['timestamp']}] {cmd['command']}\n")
        
        return str(export_path)

    def manage(self):
        """Einfaches Session-Management-Menü"""
        while True:
            print("\n--- SESSION MANAGEMENT ---")
            print("1. List Sessions")
            print("2. List Active Sessions")
            print("3. View Session Details")
            print("4. End Session")
            print("5. Export Session")
            print("6. Cleanup Old Sessions")
            print("7. Back")

            choice = input("\nSelect option: ").strip()

            if choice == "1":
                sessions = self.list_sessions()
                if not sessions:
                    print("No sessions found.")
                else:
                    for s in sessions:
                        print(f"- {s['id']} | {s['tool']} | {s['target']} | {s['status']}")
            elif choice == "2":
                active = self.get_active_sessions()
                if not active:
                    print("No active sessions.")
                else:
                    for sid, s in active.items():
                        print(f"- {sid} | {s['tool']} | {s['target']} | {s['status']}")
            elif choice == "3":
                sid = input("Session ID: ").strip()
                session = self.get_session(sid)
                if not session:
                    print("Session not found.")
                else:
                    report = self.generate_session_report(sid)
                    for k, v in report.items():
                        print(f"{k}: {v}")
            elif choice == "4":
                sid = input("Session ID to end: ").strip()
                if self.end_session(sid):
                    print("Session ended.")
                else:
                    print("Session not found.")
            elif choice == "5":
                sid = input("Session ID to export: ").strip()
                fmt = input("Format (json/txt) [json]: ").strip().lower() or "json"
                path = self.export_session(sid, format=fmt)
                if path:
                    print(f"Exported to: {path}")
                else:
                    print("Session not found.")
            elif choice == "6":
                days_raw = input("Delete sessions older than days [30]: ").strip()
                days = 30
                if days_raw.isdigit():
                    days = int(days_raw)
                cleaned = self.cleanup_old_sessions(days=days)
                print(f"Cleaned {cleaned} sessions.")
            elif choice == "7":
                break
