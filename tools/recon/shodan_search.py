#!/usr/bin/env python3
import json

try:
    import shodan
except Exception:
    shodan = None

from core.api_manager import APIManager

class ShodanSearch:
    def __init__(self):
        if shodan is None:
            raise ImportError("Optional dependency 'shodan' is not installed.")
        api_mgr = APIManager()
        key = api_mgr.get("shodan")
        if not key:
            raise ValueError("Shodan API-Key nicht gefunden.")
        self.api = shodan.Shodan(key)

    def search(self, query):
        try:
            results = self.api.search(query)
            return results
        except shodan.APIError as e:
            return {"error": str(e)}

def main(args=None):
    import sys
    if len(sys.argv) < 2:
        print("Usage: shodan_search.py <query>")
        return
    try:
        ss = ShodanSearch()
        res = ss.search(sys.argv[1])
        print(json.dumps(res, indent=2))
    except Exception as exc:
        print(f"Error: {exc}")

if __name__ == "__main__":
    main()
