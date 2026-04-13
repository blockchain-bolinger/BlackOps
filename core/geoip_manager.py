#!/usr/bin/env python3
"""Zentraler GeoIP-Manager für das BlackOps Framework."""

import geoip2.database
from pathlib import Path

class GeoIPManager:
    """Verwaltet den Zugriff auf die GeoLite2-Datenbanken."""

    def __init__(self):
        base_dir = Path(__file__).parent.parent
        self.city_db_path = base_dir / "data" / "geoip" / "GeoLite2-City.mmdb"
        self.country_db_path = base_dir / "data" / "geoip" / "GeoLite2-Country.mmdb"
        self.city_reader = None
        self.country_reader = None

    def _get_city_reader(self):
        if self.city_reader is None and self.city_db_path.exists():
            self.city_reader = geoip2.database.Reader(str(self.city_db_path))
        return self.city_reader

    def _get_country_reader(self):
        if self.country_reader is None and self.country_db_path.exists():
            self.country_reader = geoip2.database.Reader(str(self.country_db_path))
        return self.country_reader

    def get_city_info(self, ip_address: str) -> dict:
        """Gibt detaillierte Standortdaten für eine IP-Adresse zurück."""
        reader = self._get_city_reader()
        if not reader:
            return {"error": "City-Datenbank nicht gefunden"}

        try:
            response = reader.city(ip_address)
            return {
                "country": response.country.name,
                "country_code": response.country.iso_code,
                "city": response.city.name,
                "postal_code": response.postal.code,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "time_zone": response.location.time_zone
            }
        except Exception as e:
            return {"error": str(e)}

    def get_country_info(self, ip_address: str) -> dict:
        """Gibt Ländername und -code für eine IP-Adresse zurück."""
        reader = self._get_country_reader()
        if not reader:
            return {"error": "Country-Datenbank nicht gefunden"}

        try:
            response = reader.country(ip_address)
            return {
                "country": response.country.name,
                "country_code": response.country.iso_code
            }
        except Exception as e:
            return {"error": str(e)}
