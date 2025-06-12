# Import StreamController modules
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.InputBases import ActionCore

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

from com_buggex_pw_noise_gate.helpers import consts as Consts

from loguru import logger as log

# TODO what shoud be in settings? step? more?

class Dial(ActionCore):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.param_name = Consts.Paramerters.THRESHOLD
        self.param_value = "N/A"
        self.param_step = Consts.ParamertersDefaultStep[self.param_name]

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

    def __del__(self):
        log.debug("Dial DEL")

    def get_config_rows(self) -> list:
        # Parameter selector
        self.ui_param_model = Gtk.StringList().new(Consts.Paramerters.list()[1:])
        self.ui_param_selector = Adw.ComboRow(model=self.ui_param_model, title="Parameter")
        self.ui_param_selector.connect("notify::selected", self.on_param_changed)

        # Parameter step size
        self.ui_step_size = Adw.SpinRow.new_with_range(min=1, max=100, step=1)
        self.ui_step_size.set_title("Step Size")
        self.ui_step_size.set_value(Consts.ParamertersDefaultStep[Consts.Paramerters.THRESHOLD]) # TODO
        self.ui_step_size.connect("notify::value", self.on_step_size_changed)

        return [self.ui_param_selector, self.ui_step_size]
    
    def on_param_changed(self, combo, data):
        param = self.ui_param_model.get_item(self.ui_param_selector.get_selected())
        if param is None:
            return
        
        self.param_name = param.get_string()
        
        self.ui_step_size.set_value(Consts.ParamertersDefaultStep[self.param_name])
        self.set_top_label(Consts.ParamertersTitle[self.param_name])

    def on_step_size_changed(self, control, param):
        self.param_step = self.ui_step_size.get_value_as_int()
    
    def on_turn_ccw(self):
        self.plugin_base.backend.dec_param(self.param_name, self.param_step)
    
    def on_turn_cw(self):
        self.plugin_base.backend.inc_param(self.param_name, self.param_step)

    def on_param_callback(self, param, value):
        if param != self.param_name:
            return
        
        self.param_value = int(float(value))
        self.update_value_label()

    def on_ready(self):
        self.plugin_base.backend.add_callback(self.on_param_callback)

        # TODO request current value from backend

    def on_update(self):
        self.set_top_label(text=Consts.ParamertersTitle[self.param_name])
        self.update_value_label()

    def update_value_label(self):
        self.set_bottom_label(text=str(self.param_value) + " " + Consts.ParamertersUnit[self.param_name])
        
