# Import StreamController modules
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.InputBases import ActionCore

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

class Dial(ActionCore):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_event_assigner(EventAssigner(
            id="dial_ccw",
            ui_label="Dial Turn Down",
            default_event=Input.Dial.Events.TURN_CCW,
            callback=lambda data : self.on_turn_ccw()
        ))

        self.add_event_assigner(EventAssigner(
            id="dial_cw",
            ui_label="Dial Turn Down",
            default_event=Input.Dial.Events.TURN_CW,
            callback=lambda data : self.on_turn_cw()
        ))

    def get_config_rows(self) -> list:
        return []
    
    def on_turn_ccw(self):
        self.plugin_base.backend.dec_threshold()
    
    def on_turn_cw(self):
        self.plugin_base.backend.inc_threshold()

    def on_message(self, message):
        print("on_message {}\n", message)

    def on_ready(self):
        print("on_ready {}\n", self.plugin_base.backend)
        self.plugin_base.backend.add_callback(self.on_message)
        
