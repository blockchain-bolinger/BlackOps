#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

class WordlistGenerator:
    @staticmethod
    def from_website(url):
        """Extrahiert Wörter aus einer Webseite (einfach)."""
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text()
            words = re.findall(r'\b[a-zA-Z]{4,15}\b', text)
            unique = sorted(set(words))
            return unique
        except Exception as e:
            print(f"Fehler: {e}")
            return []

if __name__ == "__main__":
    wl = WordlistGenerator()
    words = wl.from_website("https://example.com")
    for w in words[:20]:
        print(w)