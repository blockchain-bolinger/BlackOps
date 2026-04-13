"""
Progress Bar Utilities für Black Ops Framework
"""

import sys
import time
from typing import Optional
from threading import Thread, Event

class ProgressBar:
    """Fortschrittsbalken mit Threading"""
    
    def __init__(self, total: int, description: str = "Progress",
                 bar_length: int = 40):
        self.total = total
        self.description = description
        self.bar_length = bar_length
        self.current = 0
        self.start_time = None
        self.is_running = False
        self.thread = None
        self.stop_event = Event()
    
    def start(self):
        """Startet Fortschrittsbalken"""
        self.start_time = time.time()
        self.is_running = True
        self.stop_event.clear()
        
        self.thread = Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
    
    def update(self, value: int = 1):
        """Aktualisiert Fortschritt"""
        self.current = min(self.current + value, self.total)
    
    def _animate(self):
        """Animiert Fortschrittsbalken"""
        while not self.stop_event.is_set() and self.current < self.total:
            self._print_progress()
            time.sleep(0.1)
        
        # Final update
        self._print_progress()
        print()
    
    def _print_progress(self):
        """Druckt Fortschritt"""
        elapsed = time.time() - self.start_time
        percent = self.current / self.total
        
        # Calculate ETA
        if percent > 0:
            eta = (elapsed / percent) - elapsed
            eta_str = f"ETA: {self._format_time(eta)}"
        else:
            eta_str = "ETA: --:--"
        
        # Calculate speed
        speed = self.current / elapsed if elapsed > 0 else 0
        
        # Create bar
        filled_length = int(self.bar_length * percent)
        bar = '█' * filled_length + '░' * (self.bar_length - filled_length)
        
        # Format progress
        progress_str = (f"\r{self.description}: "
                       f"|{bar}| "
                       f"{self.current}/{self.total} "
                       f"({percent:.1%}) "
                       f"{self._format_time(elapsed)} "
                       f"{eta_str} "
                       f"({speed:.1f}/s)")
        
        sys.stdout.write(progress_str)
        sys.stdout.flush()
    
    def _format_time(self, seconds: float) -> str:
        """Formatiert Zeit"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def finish(self):
        """Beendet Fortschrittsbalken"""
        self.current = self.total
        self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=1)
        
        self.is_running = False
    
    def __enter__(self):
        """Context Manager Enter"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager Exit"""
        self.finish()


class Spinner:
    """Lade-Spinner"""
    
    def __init__(self, message: str = "Loading"):
        self.message = message
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.is_running = False
        self.thread = None
        self.stop_event = Event()
    
    def start(self):
        """Startet Spinner"""
        self.is_running = True
        self.stop_event.clear()
        
        self.thread = Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
    
    def _animate(self):
        """Animiert Spinner"""
        i = 0
        while not self.stop_event.is_set():
            sys.stdout.write(f"\r{self.message} {self.spinner_chars[i % len(self.spinner_chars)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
        sys.stdout.flush()
    
    def stop(self):
        """Stoppt Spinner"""
        self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=1)
        
        self.is_running = False
    
    def __enter__(self):
        """Context Manager Enter"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager Exit"""
        self.stop()


class MultiProgressBar:
    """Mehrere Fortschrittsbalken"""
    
    def __init__(self, total_bars: int):
        self.bars = []
        self.total_bars = total_bars
        self.lines_printed = 0
    
    def add_bar(self, description: str, total: int) -> int:
        """Fügt Balken hinzu"""
        bar_id = len(self.bars)
        self.bars.append({
            'id': bar_id,
            'description': description,
            'total': total,
            'current': 0,
            'start_time': time.time()
        })
        
        return bar_id
    
    def update_bar(self, bar_id: int, value: int = 1):
        """Aktualisiert Balken"""
        if bar_id < len(self.bars):
            self.bars[bar_id]['current'] = min(
                self.bars[bar_id]['current'] + value,
                self.bars[bar_id]['total']
            )
    
    def print_all(self):
        """Druckt alle Balken"""
        # Move cursor up
        if self.lines_printed > 0:
            sys.stdout.write(f"\033[{self.lines_printed}A")
        
        output_lines = []
        
        for bar in self.bars:
            percent = bar['current'] / bar['total']
            filled_length = int(30 * percent)
            bar_str = '█' * filled_length + '░' * (30 - filled_length)
            
            elapsed = time.time() - bar['start_time']
            
            line = (f"{bar['description']}: "
                   f"|{bar_str}| "
                   f"{bar['current']}/{bar['total']} "
                   f"({percent:.1%}) "
                   f"{elapsed:.1f}s")
            
            output_lines.append(line)
        
        # Print all bars
        for line in output_lines:
            print(line)
        
        self.lines_printed = len(output_lines)
    
    def finish(self):
        """Beendet alle Balken"""
        for bar in self.bars:
            bar['current'] = bar['total']
        
        self.print_all()
        print()