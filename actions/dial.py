# Import StreamController modules
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.InputBases import ActionCore

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

from data.plugins.com_buggex_pw_noise_gate.helpers import parameters as Params
from data.plugins.com_buggex_pw_noise_gate.helpers import settings as Settings

from loguru import logger as log

import os

# TODO add a custom label for the toggle action
 
class Dial(ActionCore):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.param_name = Params.DialParameters.THRESHOLD
        self.param_value = "N/A"
        self.param_step = Params.DialParametersDefaultStep[self.param_name]

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
        # Parameter selector
        self.ui_param_model = Gtk.StringList().new(Params.DialParameters.list())
        self.ui_param_selector = Adw.ComboRow(model=self.ui_param_model, title="Parameter")
        self.ui_param_selector.set_selected(self.ui_param_model.find(self.param_name))
        self.ui_param_selector.connect("notify::selected", self.on_param_changed)

        # Parameter step size
        self.ui_step_size = Adw.SpinRow.new_with_range(min=1, max=100, step=1)
        self.ui_step_size.set_title("Step Size")
        self.ui_step_size.set_value(self.param_step)
        self.ui_step_size.connect("notify::value", self.on_step_size_changed)

        # Update UI elements
        self.on_update()

        return [self.ui_param_selector, self.ui_step_size]
    
    def on_param_changed(self, combo, data):
        param = self.ui_param_model.get_item(self.ui_param_selector.get_selected())
        if param is None:
            return
        
        self.param_name = param.get_string()
        self.ui_step_size.set_value(Params.DialParametersDefaultStep[self.param_name])

        settings = self.get_settings()
        settings[Settings.SETTING_PARAMETER_NAME] = self.param_name
        self.set_settings(settings)

        self.plugin_base.backend.request_param(self.param_name)

        self.update_title()        

    def on_step_size_changed(self, control, param):
        self.param_step = int(self.ui_step_size.get_value())
        
        settings = self.get_settings()
        settings[Settings.SETTING_PARAMETER_STEP] = self.param_step
        self.set_settings(settings)        
    
    def on_turn_ccw(self):
        self.plugin_base.backend.dec_param(self.param_name, self.param_step)
    
    def on_turn_cw(self):
        self.plugin_base.backend.inc_param(self.param_name, self.param_step)

    def on_param_callback(self, param, value):
        if param != self.param_name:
            return
        
        self.param_value = int(float(value))
        self.update_value_label()

    def load_config_values(self):
        settings = self.get_settings()
        
        param_name = settings.get(Settings.SETTING_PARAMETER_NAME)
        if param_name is not None:
            self.param_name = param_name
        else:
            settings[Settings.SETTING_PARAMETER_NAME] = param_name

        param_step = settings.get(Settings.SETTING_PARAMETER_STEP)
        if param_step is not None:
            self.param_step = param_step
        else:
            settings[Settings.SETTING_PARAMETER_STEP] = param_step
        
        self.set_settings(settings)

    def on_ready(self):
        self.load_config_values()
        self.plugin_base.backend.add_callback(self.on_param_callback)
        self.plugin_base.backend.request_param(self.param_name)

    def on_update(self):
        self.update_title()
        self.update_value_label()
        self.update_icon()

    def on_remove(self):
        super().on_remove()
        self.plugin_base.backend.remove_callback(self.on_param_callback)

    def update_title(self):
        self.set_top_label(text=Params.DialParametersTitle[self.param_name])

    def update_value_label(self):
        value_text = str(self.param_value)
        if value_text != "N/A":
            value_text += " " + Params.DialParametersUnit[self.param_name]
        self.set_bottom_label(text=value_text)

    def update_icon(self):
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "param.svg")
        self.set_media(media_path=icon_path, size = 2.0)
        
