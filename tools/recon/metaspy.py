import argparse
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

class MetaSpy:
    def __init__(self):
        self.banner()

    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(rf"""{Fore.MAGENTA}
    __  ___      __aSsz   _____            
   /  |/  /___  / /_____ / ___/____  __  __
  / /|_/ / _ \/ __/ __ \\__ \/ __ \/ / / /
 / /  / /  __/ /_/ /_/ /__/ / /_/ / /_/ / 
/_/  /_/\___/\__/\__,_/____/ .___/\__, /  
                          /_/    /____/   
{Fore.WHITE}   >> IMAGE FORENSICS & GPS EXTRACTOR <<
""")

    def decimal_coords(self, coords, ref):
        decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
        if ref == "S" or ref == "W":
            decimal_degrees = -decimal_degrees
        return decimal_degrees

    def analyze_image(self, image_path):
        print(f"{Fore.WHITE}[*] Analysiere: {Fore.YELLOW}{image_path}")
        
        try:
            from exif import Image
            with open(image_path, 'rb') as src:
                img = Image(src)
        except ImportError:
            print(f"{Fore.RED}[ERROR] Missing dependency: exif. Install with: pip install exif")
            return
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Datei konnte nicht gelesen werden: {e}")
            return

        if not img.has_exif:
            print(f"{Fore.RED}[-] Das Bild enthält keine EXIF-Metadaten.")
            return

        print(f"\n{Fore.CYAN}[INFO] Basis Daten:")
        try:
            print(f"  Kamera:     {img.make} {img.model}")
            print(f"  Datum:      {img.datetime_original}")
            print(f"  Software:   {img.software}")
        except AttributeError:
            print(f"  {Fore.WHITE}(Teilweise fehlend)")

        print(f"\n{Fore.CYAN}[INFO] GPS Daten:")
        try:
            lat = self.decimal_coords(img.gps_latitude, img.gps_latitude_ref)
            lon = self.decimal_coords(img.gps_longitude, img.gps_longitude_ref)
            
            print(f"  {Fore.GREEN}Breitengrad: {lat}")
            print(f"  {Fore.GREEN}Längengrad:  {lon}")
            print(f"\n{Fore.YELLOW}  [MAPS LINK] https://www.google.com/maps?q={lat},{lon}")
        except AttributeError:
            print(f"  {Fore.RED}[-] Keine GPS Koordinaten im Bild gefunden.")

    def run(self):
        path = input(f"{Fore.GREEN}[?] Pfad zum Bild (z.B. /home/kali/foto.jpg): ").strip().strip("'")
        if os.path.exists(path):
            self.analyze_image(path)
        else:
            print(f"{Fore.RED}[ERROR] Datei existiert nicht.")
        
        input(f"\n{Fore.WHITE}[ENTER] Zurück...")

if __name__ == "__main__":
    tool = MetaSpy()
    tool.run()
