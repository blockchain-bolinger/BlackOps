"""
Color Output Utilities für Black Ops Framework
"""

import sys
from typing import Optional
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

class ColorOutput:
    """Farbige Konsolenausgabe"""
    
    @staticmethod
    def print_success(message: str):
        """Grüne Erfolgsmeldung"""
        print(f"{Fore.GREEN}[✓]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def print_error(message: str):
        """Rote Fehlermeldung"""
        print(f"{Fore.RED}[✗]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Gelbe Warnmeldung"""
        print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def print_info(message: str):
        """Blaue Infomeldung"""
        print(f"{Fore.BLUE}[i]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def print_debug(message: str):
        """Cyan Debugmeldung"""
        print(f"{Fore.CYAN}[D]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def print_critical(message: str):
        """Rote kritische Meldung"""
        print(f"{Fore.RED}{Style.BRIGHT}[CRITICAL]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def print_header(text: str, char: str = "=", color: str = "cyan"):
        """Header mit Linie"""
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE
        }
        
        color_code = colors.get(color, Fore.CYAN)
        
        line = char * 60
        print(f"\n{color_code}{line}{Style.RESET_ALL}")
        print(f"{color_code}{text.center(60)}{Style.RESET_ALL}")
        print(f"{color_code}{line}{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_table(data: list, headers: list = None, 
                   col_widths: list = None):
        """Druckt Tabelle mit Farben"""
        if not data:
            return
        
        if headers is None:
            headers = [f"Column {i+1}" for i in range(len(data[0]))]
        
        if col_widths is None:
            # Auto-calculate column widths
            col_widths = []
            for i in range(len(headers)):
                max_len = len(str(headers[i]))
                for row in data:
                    if i < len(row):
                        max_len = max(max_len, len(str(row[i])))
                col_widths.append(max_len + 2)
        
        # Print header
        header_line = "│ "
        for i, header in enumerate(headers):
            header_line += f"{Fore.CYAN}{header:<{col_widths[i]}}{Style.RESET_ALL}│ "
        
        top_border = "┌" + "".join(["─" * (w + 2) + "┬" for w in col_widths])[:-1] + "┐"
        middle_border = "├" + "".join(["─" * (w + 2) + "┼" for w in col_widths])[:-1] + "┤"
        bottom_border = "└" + "".join(["─" * (w + 2) + "┴" for w in col_widths])[:-1] + "┘"
        
        print(top_border)
        print(header_line)
        print(middle_border)
        
        # Print rows
        for row in data:
            row_line = "│ "
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_line += f"{cell:<{col_widths[i]}}│ "
            print(row_line)
        
        print(bottom_border)
    
    @staticmethod
    def input_colored(prompt: str, color: str = "yellow") -> str:
        """Farbige Eingabeaufforderung"""
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'cyan': Fore.CYAN
        }
        
        color_code = colors.get(color, Fore.YELLOW)
        
        sys.stdout.write(f"{color_code}{prompt}{Style.RESET_ALL}")
        sys.stdout.flush()
        
        return input()
    
    @staticmethod
    def print_progress_bar(iteration: int, total: int, 
                          prefix: str = '', suffix: str = '',
                          length: int = 50, fill: str = '█'):
        """Fortschrittsbalken"""
        percent = f"{100 * (iteration / float(total)):.1f}"
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        
        sys.stdout.write(f'\r{prefix} │{Fore.GREEN}{bar}{Style.RESET_ALL}│ {percent}% {suffix}')
        sys.stdout.flush()
        
        if iteration == total:
            print()
    
    @staticmethod
    def print_bullet_list(items: list, color: str = "cyan"):
        """Bullet List"""
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'cyan': Fore.CYAN,
            'magenta': Fore.MAGENTA
        }
        
        color_code = colors.get(color, Fore.CYAN)
        
        for item in items:
            print(f"{color_code}•{Style.RESET_ALL} {item}")
    
    @staticmethod
    def highlight_text(text: str, highlight: str, 
                      highlight_color: str = "red",
                      text_color: str = "white"):
        """Hebt Text hervor"""
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE
        }
        
        text_color_code = colors.get(text_color, Fore.WHITE)
        highlight_color_code = colors.get(highlight_color, Fore.RED)
        
        highlighted = text.replace(
            highlight, 
            f"{highlight_color_code}{highlight}{text_color_code}"
        )
        
        print(f"{text_color_code}{highlighted}{Style.RESET_ALL}")