from streamcontroller_plugin_tools import BackendBase
from loguru import logger as log

import socket

# To get access to plugin files
import sys
from pathlib import Path
ABSOLUTE_PLUGIN_PATH = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, ABSOLUTE_PLUGIN_PATH)

class Backend(BackendBase):
    def __init__(self):
        super().__init__()
        self.port = 8080
        self.host = "127.0.0.1"
        self.socket = socket.socket()    

    def set_port(self, port):
        self.port = port

    def send_data(self, data):
        self.socket.connect((self.host, self.port)) 
        self.socket.send(data.encode());
        self.socket.close()

backend = Backend()
