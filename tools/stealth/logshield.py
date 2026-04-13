#!/usr/bin/env python3
"""
LogShield - Echtzeit-Log-Überwachung mit Alarmfunktion
"""

import argparse
import time
import re
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import Fore, init

init(autoreset=True)

class LogHandler(FileSystemEventHandler):
    def __init__(self, patterns, callback):
        self.patterns = patterns
        self.callback = callback
        self.file_position = {}
    
    def on_modified(self, event):
        if not event.is_directory:
            self.process_log(event.src_path)
    
    def process_log(self, logfile):
        if logfile not in self.file_position:
            self.file_position[logfile] = 0
        with open(logfile, 'r') as f:
            f.seek(self.file_position[logfile])
            for line in f:
                for pattern in self.patterns:
                    if re.search(pattern, line, re.I):
                        self.callback(logfile, line)
            self.file_position[logfile] = f.tell()

class LogShield:
    def __init__(self, log_files, patterns, alert_cmd=None):
        self.log_files = log_files
        self.patterns = patterns
        self.alert_cmd = alert_cmd
    
    def print_banner(self):
        print(rf"""{Fore.GREEN}
   _                    _     _     _      
  | |    ___   ___  ___| |__ (_)___| |__   
  | |   / _ \ / _ \/ __| '_ \| / __| '_ \  
  | |__| (_) | (_) \__ \ | | | \__ \ | | | 
  |_____\___/ \___/|___/_| |_|_|___/_| |_| 
{Fore.WHITE}   >> REAL-TIME LOG MONITOR v1.0 <<
        """)
    
    def alert(self, logfile, line):
        print(f"{Fore.RED}[ALERT] {logfile}: {line.strip()}")
        if self.alert_cmd:
            import subprocess
            subprocess.Popen(self.alert_cmd, shell=True)
    
    def run(self):
        self.print_banner()
        event_handler = LogHandler(self.patterns, self.alert)
        observer = Observer()
        for logfile in self.log_files:
            observer.schedule(event_handler, path=logfile, recursive=False)
        observer.start()
        print(f"{Fore.GREEN}[*] Überwache: {', '.join(self.log_files)}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

def main():
    parser = argparse.ArgumentParser(description="LogShield")
    parser.add_argument("-l", "--logs", nargs='+', required=True, help="Log-Dateien")
    parser.add_argument("-p", "--patterns", nargs='+', default=["failed", "error", "attack", "unauthorized"])
    parser.add_argument("--alert-cmd", help="Befehl bei Alarm (z.B. 'notify-send Alert')")
    args = parser.parse_args()
    
    shield = LogShield(args.logs, args.patterns, args.alert_cmd)
    shield.run()

if __name__ == "__main__":
    main()
