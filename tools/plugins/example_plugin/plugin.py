from core.plugin_manager import PluginInterface

class ExamplePlugin(PluginInterface):
    def name(self):
        return "ExamplePlugin"

    def description(self):
        return "Ein Beispiel-Plugin."

    def run(self, **kwargs):
        print("Beispiel-Plugin wird ausgeführt...")
        print("Erhaltene Argumente:", kwargs)
        return {"status": "ok"}