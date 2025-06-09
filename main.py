# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder

import os

# Import actions
from .actions import Dial

class PluginTemplate(PluginBase):
    def __init__(self):
        super().__init__()

        # Start backend
        self.launch_backend(
            os.path.join(self.PATH, "backend", "backend.py"),
            os.path.join(self.PATH, "backend", ".venv"),
            open_in_terminal=False,
        )
        self.wait_for_backend(tries=5)

        ## Register actions
        self.simple_action_holder = ActionHolder(
            plugin_base = self,
            action_base = Dial,
            action_id = "com_buggex_pw_noise_gate::Dial",
            action_name = "Dial",
        )
        self.add_action_holder(self.simple_action_holder)

        # Register plugin
        self.register(
            plugin_name = "Pipewire Noise Gate Control",
            github_repo = "https://github.com/StreamController/PluginTemplate",
            plugin_version = "1.0.0",
            app_version = "1.1.1-alpha"
        )