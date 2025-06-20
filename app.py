from nicegui import ui
import json
import importlib.util
import os

# Load config
with open('data/config/config.json') as f:
    config = json.load(f)

# Dynamically import Home plugin as the home page
plugin_path = os.path.join("data/plugins", config['home'])
plugin_spec = importlib.util.spec_from_file_location(config['home'], f"{plugin_path}.py")
plugin = importlib.util.module_from_spec(plugin_spec)
plugin_spec.loader.exec_module(plugin)

ui.run(title=config['title'])
