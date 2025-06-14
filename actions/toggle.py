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

# TODO add a custom label for the toggle action
 
class Toggle(ActionCore):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.param_name = Params.ToogleParameters.ENABLED
        self.param_value = "N/A"

        self.add_event_assigner(EventAssigner(
            id="toggle",
            ui_label="Toggle",
            default_event=Input.Key.Events.UP,
            callback=lambda data : self.on_toggle()
        ))

    def get_config_rows(self) -> list:
        # Parameter selector
        self.ui_param_model = Gtk.StringList().new(Params.ToogleParameters.list())
        self.ui_param_selector = Adw.ComboRow(model=self.ui_param_model, title="Parameter")
        self.ui_param_selector.set_selected(self.ui_param_model.find(self.param_name))
        self.ui_param_selector.connect("notify::selected", self.on_param_changed)

        # Update UI elements
        self.on_update()

        return [self.ui_param_selector]
    
    def on_param_changed(self, combo, data):
        param = self.ui_param_model.get_item(self.ui_param_selector.get_selected())
        if param is None:
            return
        
        self.param_name = param.get_string()

        settings = self.get_settings()
        settings[Settings.SETTING_PARAMETER_NAME] = self.param_name
        self.set_settings(settings)

        self.plugin_base.backend.request_param(self.param_name)

        self.update_title()        


    def on_toggle(self):
        self.plugin_base.backend.toggle_param(self.param_name)
    
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
        
        self.set_settings(settings)

    def on_ready(self):
        self.load_config_values()
        self.plugin_base.backend.add_callback(self.on_param_callback)
        self.plugin_base.backend.request_param(self.param_name)

    def on_update(self):
        self.update_title()
        self.update_value_label()

    def on_remove(self):
        super().on_remove()
        self.plugin_base.backend.remove_callback(self.on_param_callback)

    def update_title(self):
        self.set_top_label(text=Params.ToogleParametersTitle[self.param_name])

    def update_value_label(self):
        value_text = str(self.param_value)
        if value_text != "N/A":
            value_text = 'OFF' if int(self.param_value) == 0 else 'ON' # TODO translate this
        self.set_bottom_label(text=value_text)
        
