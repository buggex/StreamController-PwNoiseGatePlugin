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
        self.callbacks = []

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

    def inc_param(self, param_name, param_step):
        self.send_data(param_name + "|" + str(param_step))

    def dec_param(self, param_name, param_step):
        self.send_data(param_name + "|-" + str(param_step))

    def send_data(self, data):
        log.debug("Puttong on queue: {}", data)
        self.outgoing_queue.put(data)

    def add_callback(self, callback: Callable):
        self.callbacks.append(callback)

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
                for cmd in received_data.decode().split("\n"):
                    cmd_strip = cmd.strip()
                    if cmd_strip == "":
                        continue
                    log.debug("Received command: {}", cmd_strip)

                    cmd_split = cmd_strip.split("|")
                    if len(cmd_split) != 2:
                        log.error("Invalid command format: {}", cmd_strip)
                        continue

                    if self.callbacks:
                        for callback in self.callbacks:
                            if callable(callback):
                                callback(cmd_split[0], cmd_split[1])
                            else:
                                log.error("Callback is not callable: {}", callback)

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
