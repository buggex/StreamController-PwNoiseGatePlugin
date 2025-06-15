# Import StreamController modules
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.InputBases import ActionCore

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

from com_buggex_pw_noise_gate.helpers import parameters as Params
from com_buggex_pw_noise_gate.helpers import settings as Settings

from loguru import logger as log
import os

# TODO add a custom label for the toggle action
 
class Toggle(ActionCore):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.param_name = Params.ToogleParameters.ENABLED
        self.param_value = "N/A"
        self.param_show_name = False
        self.param_show_value = False

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
        self.ui_param_selector.connect("notify::selected", 
            lambda combo, args: self.on_param_changed(combo.get_model().get_item(combo.get_selected()).get_string()))

        # Show parameter name
        self.ui_param_show_name = Adw.SwitchRow(title="Show Name")
        self.ui_param_show_name.connect("notify::active", lambda row, args: self.set_show_title_label(row.get_active()))

        # Show parameter value
        self.ui_param_show_value = Adw.SwitchRow(title="Show Value")
        self.ui_param_show_value.connect("notify::active", lambda row, args: self.set_show_value_label(row.get_active()))

        # Update UI elements
        self.on_update()

        return [self.ui_param_selector, self.ui_param_show_name, self.ui_param_show_value]
    
    def on_param_changed(self, selected):
        self.param_name = selected

        settings = self.get_settings()
        settings[Settings.SETTING_PARAMETER_NAME] = self.param_name
        self.set_settings(settings)

        self.plugin_base.backend.request_param(self.param_name)

        self.update_title()        

    def set_show_title_label(self, show: bool):
        self.param_show_name = show
        
        settings = self.get_settings()
        settings[Settings.SETTING_SHOW_PARAMETER_NAME] = show
        self.set_settings(settings)

        self.update_title()

    def set_show_value_label(self, show: bool):
        self.param_show_value = show
        
        settings = self.get_settings()
        settings[Settings.SETTING_SHOW_PARAMETER_VALUE] = show
        self.set_settings(settings)

        self.update_value_label()

    def on_toggle(self):
        self.plugin_base.backend.toggle_param(self.param_name)
    
    def on_param_callback(self, param, value):
        if param != self.param_name:
            return
        
        self.param_value = int(float(value))
        self.update_value_label()
        self.update_icon()

    def load_config_values(self):
        self.param_name = self.get_setting(Settings.SETTING_PARAMETER_NAME, Params.ToogleParameters.ENABLED)
        self.param_show_name = self.get_setting(Settings.SETTING_SHOW_PARAMETER_NAME, False)
        self.param_show_value = self.get_setting(Settings.SETTING_SHOW_PARAMETER_VALUE, False)

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
        if self.param_show_name:
            self.set_top_label(text=Params.ToogleParametersTitle[self.param_name])
        else:
            self.set_top_label(text="")
        

    def update_value_label(self):
        if self.param_show_value:
            value_text = str(self.param_value)
            if value_text != "N/A":
                value_text = 'OFF' if int(self.param_value) == 0 else 'ON' # TODO translate this
            self.set_bottom_label(text=value_text)
        else:
            self.set_bottom_label(text="")

    def update_icon(self):
        if str(self.param_value).isnumeric() and int(self.param_value) == 1:
            icon_path = os.path.join(self.plugin_base.PATH, "assets", "gate_on.svg")
        else:
            icon_path = os.path.join(self.plugin_base.PATH, "assets", "gate_off.svg")
        self.set_media(media_path=icon_path, size = 0.8)
        
    def get_setting(self, key : str, default=None):
        settings = self.get_settings()
        value = settings.get(key)
        if value is None:
            return default
        return value