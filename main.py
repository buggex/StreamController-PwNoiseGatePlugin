# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

import os
import sys
from pathlib import Path

from loguru import logger as log

# Add plugin to sys.paths
ABSOLUTE_PLUGIN_PATH = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, ABSOLUTE_PLUGIN_PATH)

# Import actions
from .actions.dial import Dial
from .actions.toggle import Toggle

# Import backend
from .backend.backend import Backend

class PwNoiseGate(PluginBase):
    def __init__(self):
        super().__init__()

        # Start backend
        self.backend = Backend()

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

        self.toggle_holder = ActionHolder(
            plugin_base=self,
            action_base=Toggle,
            action_id_suffix="Toggle",
            action_name="Toggle",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.SUPPORTED
            }
        )
        self.add_action_holder(self.toggle_holder)

        # Register plugin
        self.register(
            plugin_name = "Pipewire Noise Gate Control",
            github_repo = "https://github.com/StreamController/PluginTemplate",
            plugin_version = "1.0.0",
            app_version = "1.1.1-alpha"
        )
    
    def __del__(self):
        log.debug("Cleaning up Pipewire Noise Gate plugin...")
        if self.backend:
            self.backend.release()