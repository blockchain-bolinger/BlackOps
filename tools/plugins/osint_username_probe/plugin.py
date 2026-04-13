import requests

from core.plugin_manager import PluginInterface


class OsintUsernameProbePlugin(PluginInterface):
    version = "1.0.0"
    api_version = 1

    SITE_MAP = {
        "github": "https://github.com/{username}",
        "gitlab": "https://gitlab.com/{username}",
        "reddit": "https://www.reddit.com/user/{username}",
        "medium": "https://medium.com/@{username}",
        "devto": "https://dev.to/{username}",
        "pinterest": "https://www.pinterest.com/{username}/",
    }

    def name(self):
        return "osint_username_probe"

    def description(self):
        return "Prueft verbreitete Plattformen auf ein gegebenes Username-Profil."

    def run(self, **kwargs):
        username = (kwargs.get("username") or "").strip()
        if not username:
            raise ValueError("Parameter 'username' ist erforderlich, z.B. username=john_doe")

        timeout = float(kwargs.get("timeout", 6))
        selected_sites = self._parse_sites(kwargs.get("sites", ""))
        results = []

        for site_name in selected_sites:
            url = self.SITE_MAP[site_name].format(username=username)
            row = {"site": site_name, "url": url}
            try:
                response = requests.get(
                    url,
                    timeout=timeout,
                    allow_redirects=True,
                    headers={"User-Agent": "BlackOps-OSINT/1.0"},
                )
                body = (response.text or "").lower()
                not_found_hints = ("not found", "doesn’t exist", "doesn't exist", "page not found")
                likely_exists = response.status_code == 200 and not any(hint in body for hint in not_found_hints)
                row.update({"status_code": response.status_code, "exists_likely": likely_exists, "final_url": response.url})
            except Exception as exc:
                row.update({"status_code": None, "exists_likely": False, "error": str(exc)})
            results.append(row)

        found = sum(1 for item in results if item.get("exists_likely"))
        return {"username": username, "checked_sites": len(results), "matches_likely": found, "results": results}

    def _parse_sites(self, raw):
        if not raw:
            return list(self.SITE_MAP.keys())
        requested = [item.strip().lower() for item in str(raw).split(",") if item.strip()]
        return [site for site in requested if site in self.SITE_MAP]

