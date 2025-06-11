# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

import os

# Import actions
from .actions.dial import Dial

class PwNoiseGate(PluginBase):
    def __init__(self):
        super().__init__()

        # Start backend
        self.launch_backend(
            os.path.join(self.PATH, "backend", "backend.py"),
            os.path.join(self.PATH, "backend", ".venv"),
            open_in_terminal=False,
        )

        # Register actions
        self.dial_holder = ActionHolder(
            plugin_base=self,
            action_base=Dial,
            action_id_suffix="Dial",
            action_name="Dial",
            action_support={
                Input.Key: ActionInputSupport.UNSUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )
        self.add_action_holder(self.dial_holder)

        # Register plugin
        self.register(
            plugin_name = "Pipewire Noise Gate Control",
            github_repo = "https://github.com/StreamController/PluginTemplate",
            plugin_version = "1.0.0",
            app_version = "1.1.1-alpha"
        )
    
    def __del__(self):
        self.backend.release()