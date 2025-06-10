from streamcontroller_plugin_tools import BackendBase
from loguru import logger as log

import socket

# To get access to plugin files
import sys
from pathlib import Path
ABSOLUTE_PLUGIN_PATH = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, ABSOLUTE_PLUGIN_PATH)

# TODO 
#  - retry connection every X seconds if lost
#  - Socket thead
#    Queue to send command to the thread
#    Mutex to send data to backend?

class Backend(BackendBase):
    def __init__(self):
        super().__init__()
        self.port = 8080
        self.host = "127.0.0.1"

        self.threshold = 0

        self.connect()

    def __del__(self):
        self.socket.close()

    def set_port(self, port):
        self.port = port

    def inc_threshold(self):
        self.send_data("threshold|1")

    def dec_threshold(self):
        self.send_data("threshold|-1")

    def connect(self):
        try:
            log.debug("Connecting to {} : {}", self.host, self.port)
            self.socket = socket.socket()
            self.socket.connect((self.host, self.port))
        except:
            log.error("Failed to connect to {}:{}", self.host, self.port)

    def send_data(self, data, tries = 3):
        if(tries < 1):
            return
        
        failed = False

        try:
            log.debug("Sending {} : {}", data, tries)
            self.socket.sendall(data.encode());
        except:
            log.error("Failed to send {} : {}", data, tries)
            failed = True

        if failed:
            self.connect()
            next_tries = tries - 1
            self.send_data(data, next_tries)

backend = Backend()
