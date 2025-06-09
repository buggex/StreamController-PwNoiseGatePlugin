from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import globals as gl
from loguru import logger as log
from fuzzywuzzy import fuzz

import os

class Dial(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def event_callback(self, event, data):
        if event == Input.Dial.Events.TURN_CW:
            #volume = inputs[index].volume.value_flat
            #olume += self.plugin_base.volume_increment

            self.plugin_base.backend.send_data("threshold=5")

        elif event == Input.Dial.Events.TURN_CCW:
            #volume = inputs[index].volume.value_flat
            #volume -= self.plugin_base.volume_increment

            self.plugin_base.backend.send_data("threshold=4")
