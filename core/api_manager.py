#!/usr/bin/env python3
from core.secrets_manager import SecretsManager

class APIManager:
    """Verwaltet API-Schlüssel über SecretsManager (Env/.env/Datei)."""

    def __init__(self, secrets_file="secrets.json"):
        self.secrets_file = secrets_file
        self.secrets = SecretsManager(path=secrets_file)

    def get(self, service):
        """Gibt den API-Key für einen Dienst zurück."""
        return (
            self.secrets.get(f"api_keys.{service}")
            or self.secrets.get(service)
            or self.secrets.get(f"{service}_api_key")
        )

    def set(self, service, api_key):
        """Speichert einen API-Key (optional)."""
        self.secrets.set(f"api_keys.{service}", api_key)
