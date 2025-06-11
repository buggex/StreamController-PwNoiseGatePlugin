from streamcontroller_plugin_tools import BackendBase
from loguru import logger as log

import socket
import threading
import queue
import time
from dataclasses import dataclass
from typing import Callable

# To get access to plugin files
import sys
from pathlib import Path
ABSOLUTE_PLUGIN_PATH = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, ABSOLUTE_PLUGIN_PATH)

# TODO 
#  - retry connection every X seconds if lost
#  - Socket thead
#     - how to handle changes to host or port? START A NEW THREAD
#     - how to send data to the backend?


class Backend(BackendBase):
    def __init__(self):
        super().__init__()
        self.host = "127.0.0.1"
        self.port = 8080
        self.quit = False
        self.outgoing_queue = queue.Queue()
        self.callback = None

        self.socket_thread = threading.Thread(target=self.socket_thread_run)
        self.socket_thread.start()

    def __del__(self):
        # TODO HOW?
        log.debug("on_disconnect 1")
        self.thread_data.quit = True
        self.socket_thread.join()
        log.debug("on_disconnect 2")

    def set_port(self, port):
        self.port = port

    def inc_threshold(self):
        self.send_data("threshold|1")

    def dec_threshold(self):
        self.send_data("threshold|-1")

    def send_data(self, data):
        log.debug("Puttong on queue: {}", data)
        self.outgoing_queue.put(data)

    def add_callback(self, callback: Callable):
        print("add_callback {}\n", callback)
        self.callback = callback

    def socket_thread_run(self):
        log.debug("Connection thread start")
        connection = socket.socket()
        connection.connect((self.host, self.port))
        
        log.debug("Connection thread start - connected")
        while True:
            if self.quit == True:
                break

            connection.settimeout(0.001)
            received_data = None
            try:
                received_data = connection.recv(1024)
            except:
                pass
            
            if received_data:
                log.debug("Received data: {} | {}", received_data, self.callback)
                if self.callback:
                    self.callback(received_data)

            while not self.outgoing_queue.empty():
                try:
                    cmd = self.outgoing_queue.get()
                    log.debug("Sending {}", cmd)
                    connection.sendall(cmd.encode());
                except:
                    log.error("Failed to send {}", cmd)

            time.sleep(0.01) # 10 ms
        
        connection.close()
        log.debug("Connection thread stop")

backend = Backend()
