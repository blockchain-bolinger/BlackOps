import hashlib
from pathlib import Path

from core.plugin_manager import PluginInterface


class FileHashPlugin(PluginInterface):
    version = "1.0.0"
    api_version = 1

    def name(self):
        return "file_hash"

    def description(self):
        return "Berechnet den Hash einer Datei (sha256, sha512, sha1 oder md5)."

    def run(self, **kwargs):
        file_path = kwargs.get("path")
        algorithm = (kwargs.get("algo") or "sha256").lower()
        allowed = {"sha256", "sha512", "sha1", "md5"}

        if not file_path:
            raise ValueError("Parameter 'path' ist erforderlich, z.B. path=README.md")
        if algorithm not in allowed:
            raise ValueError(f"Ungültiger Algorithmus '{algorithm}'. Erlaubt: {', '.join(sorted(allowed))}")

        target = Path(file_path)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"Datei nicht gefunden: {file_path}")

        hasher = hashlib.new(algorithm)
        with target.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                hasher.update(chunk)

        return {
            "path": str(target),
            "algorithm": algorithm,
            "digest": hasher.hexdigest(),
        }
