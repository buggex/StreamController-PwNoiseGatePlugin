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

from .helpers import settings as Settings

# Import gtk modules - used for settings
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

class PwNoiseGate(PluginBase):
    def __init__(self):
        super().__init__()

        # Start backend
        self.backend = Backend()

        # Load settings
        settings = self.get_settings()
        self.backend.set_host(settings.get(Settings.SETTING_HOST, "localhost"))
        self.backend.set_port(settings.get(Settings.SETTING_PORT, "50301"))
        self.set_settings(settings) # set setting if this is the first run

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

    def get_settings_area(self):
        settings = self.get_settings()
        host = settings.get(Settings.SETTING_HOST, "localhost")
        port = settings.get(Settings.SETTING_PORT, "8080")
        

        self.host_entry = Adw.EntryRow(title="Host") # TODO translate
        self.host_entry.set_text(host)
        self.host_entry.connect("notify::text", self.on_host_changed)

        self.port_entry = Adw.EntryRow(title="Port") # TODO translate
        self.port_entry.set_text(port)
        self.port_entry.connect("notify::text", self.on_port_changed)

        group = Adw.PreferencesGroup()
        group.add(self.host_entry)
        group.add(self.port_entry)
        return group

    def on_host_changed(self, entry, *args):
        host = entry.get_text()
        if host:
            self.backend.set_host(host)

            settings = self.get_settings()
            settings[Settings.SETTING_HOST] = host
            self.set_settings(settings) 

    def on_port_changed(self, entry, *args):
        port = entry.get_text()
        if port:
            self.backend.set_port(port)

            settings = self.get_settings()
            settings[Settings.SETTING_PORT] = port
            self.set_settings(settings)
