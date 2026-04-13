#!/usr/bin/env python3
"""
Plugin-Management mit Discovery, Lifecycle und API-Kompatibilitätsprüfung.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import importlib.util
import inspect
import pkgutil
from pathlib import Path
from typing import Any, Dict, Optional


PLUGIN_API_VERSION = 1


@dataclass
class PluginMetadata:
    name: str
    description: str = ""
    version: str = "0.1.0"
    api_version: int = PLUGIN_API_VERSION
    module_path: str = ""
    compatible: bool = True
    error: str = ""


class PluginInterface:
    """Jedes Plugin muss mindestens `name()` und `run()` implementieren."""

    version = "0.1.0"
    api_version = PLUGIN_API_VERSION

    def name(self) -> str:
        raise NotImplementedError

    def description(self) -> str:
        return ""

    def on_load(self, context: Optional[Dict[str, Any]] = None) -> None:
        """Optionaler Lifecycle-Hook beim Laden."""

    def on_unload(self, context: Optional[Dict[str, Any]] = None) -> None:
        """Optionaler Lifecycle-Hook beim Entladen."""

    def run(self, **kwargs) -> Any:
        raise NotImplementedError

    def get_parameters(self) -> Dict[str, Dict[str, str]]:
        """Gibt ein Schema der benötigten Parameter zurück: {'name': {'type': 'str', 'description': '...'}}"""
        return {}


class PluginManager:
    """Lädt Plugins aus `tools/plugins` mit Auto-Discovery."""

    def __init__(self, plugin_dir: str = "tools/plugins", required_api_version: int = PLUGIN_API_VERSION):
        self.plugin_dir = Path(plugin_dir)
        self.required_api_version = required_api_version
        self.plugins: Dict[str, PluginInterface] = {}
        self.metadata: Dict[str, PluginMetadata] = {}

    def _ensure_plugin_dir(self) -> None:
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        init_file = self.plugin_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("", encoding="utf-8")

    def _iter_candidate_modules(self):
        for item in pkgutil.iter_modules([str(self.plugin_dir)]):
            name = item.name
            if item.ispkg:
                yield {"name": name, "path": self.plugin_dir / name / "plugin.py", "is_file": True}
            else:
                yield {"name": name, "path": self.plugin_dir / f"{name}.py", "is_file": True}

    def _load_module(self, candidate: Dict[str, Any]):
        module_path = candidate["path"]
        if module_path.exists():
            module_name = f"blackops_plugin_{candidate['name']}"
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module, str(module_path)
        prefix = self.plugin_dir.as_posix().replace("/", ".").strip(".")
        module_name = f"{prefix}.{candidate['name']}"
        return importlib.import_module(module_name), module_name

    def _is_compatible(self, instance: PluginInterface) -> bool:
        api_version = getattr(instance, "api_version", PLUGIN_API_VERSION)
        return int(api_version) == int(self.required_api_version)

    def discover(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, PluginInterface]:
        self._ensure_plugin_dir()
        self.plugins = {}
        self.metadata = {}

        for candidate in self._iter_candidate_modules():
            default_name = candidate["name"]
            module_path = None
            try:
                module, module_path = self._load_module(candidate)
                for _, cls in inspect.getmembers(module, inspect.isclass):
                    if not issubclass(cls, PluginInterface) or cls is PluginInterface:
                        continue
                    instance = cls()
                    plugin_name = instance.name() or default_name
                    compatible = self._is_compatible(instance)
                    meta = PluginMetadata(
                        name=plugin_name,
                        description=instance.description(),
                        version=str(getattr(instance, "version", "0.1.0")),
                        api_version=int(getattr(instance, "api_version", PLUGIN_API_VERSION)),
                        module_path=module_path,
                        compatible=compatible,
                        error="" if compatible else "Incompatible plugin API version",
                    )
                    self.metadata[plugin_name] = meta
                    if not compatible:
                        continue
                    instance.on_load(context=context or {})
                    self.plugins[plugin_name] = instance
            except Exception as exc:
                self.metadata[default_name] = PluginMetadata(
                    name=default_name,
                    module_path=module_path,
                    compatible=False,
                    error=str(exc),
                )
        return self.plugins

    def unload(self, name: str, context: Optional[Dict[str, Any]] = None) -> bool:
        plugin = self.plugins.get(name)
        if not plugin:
            return False
        try:
            plugin.on_unload(context=context or {})
        finally:
            self.plugins.pop(name, None)
        return True

    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        return self.plugins.get(name)

    def list_plugins(self, include_incompatible: bool = False):
        if include_incompatible:
            return sorted(self.metadata.keys())
        return sorted(self.plugins.keys())

    def list_plugin_metadata(self):
        return {k: vars(v) for k, v in self.metadata.items()}
