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

class Backend(BackendBase):
    def __init__(self):
        super().__init__()
        self.host = "127.0.0.1"
        self.port = 8080
        self.stop_socket_thread = False
        self.outgoing_queue = queue.Queue()
        self.callbacks = []

        self.socket_thread = threading.Thread(target=self.socket_thread_run)
        self.socket_thread.start()

    def __del__(self):
        # TODO HOW?
        log.debug("__del__")
        self.thread_data.quit = True
        self.socket_thread.join()

    def set_port(self, port):
        self.port = port

    def inc_param(self, param_name, param_step):
        self.send_data(param_name + "|" + str(param_step))

    def dec_param(self, param_name, param_step):
        self.send_data(param_name + "|-" + str(param_step))

    def request_param(self, param_name):
        self.send_data(param_name + "|request")

    def send_data(self, data):
        self.outgoing_queue.put(data)

    def add_callback(self, callback: Callable):
        self.callbacks.append(callback)

    def socket_thread_run(self):
        connection = None
        current_host = self.host
        current_port = self.port
        connection = self.socket_reconnect(connection, current_host, current_port)
        
        while True:
            if self.stop_socket_thread == True:
                break

            if not self.is_socket_connected(connection):
                log.error("Socket connection lost")
                try:
                    connection = self.socket_reconnect(connection, current_host, current_port)
                    time.sleep(0.1) # Wait a bit before trying to continue
                except:
                    time.sleep(5) # Wait 5 seconds before trying to reconnect
                    continue

            if self.has_connection_parameters_changed(current_host, current_port):
                log.debug("Connection parameters changed")
                current_host = self.host
                current_port = self.port
                try:
                    connection = self.socket_reconnect(connection, current_host, current_port)
                except Exception as e:
                    log.error("Failed to reconnect: {}", e)
                    time.sleep(5)

            received_data = None
            try:
                received_data = connection.recv(1024)
            except:
                pass
            
            if received_data:
                self.socket_thread_handle_message(received_data)

            while not self.outgoing_queue.empty():
                self.socket_thread_handle_outgoing(connection)

            # Sleep thread
            time.sleep(0.01) # 10 ms
        
        connection.close()
        log.debug("Connection thread stop")

    def has_connection_parameters_changed(self, current_host, current_port):
        return self.host != current_host or self.port != current_port        
    
    def is_socket_connected(self, connection):
        try:
            connection.sendall(b'')
            return True
        except (socket.error, OSError):
            return False
        
    def socket_reconnect(self, connection, host, port):
        log.debug("Reconnecting socket...")
        try:
            connection.close()
        except:
            pass
        connection = socket.socket()
        connection.connect((host, port))
        connection.settimeout(0.001) # Connection calls should not block
        log.debug("Socket connected to {}:{}", host, port)
        return connection
    
    # handle incoming messages
    def socket_thread_handle_message(self, received_data):
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
                        try:
                            callback(cmd_split[0], cmd_split[1])
                        except Exception as e:
                            log.error("Error in callback: {} - {}", callback, e)
                    else:
                        log.error("Callback is not callable: {}", callback)
    
    # handle outgoing messages
    def socket_thread_handle_outgoing(self, connection):
        try:
            cmd = self.outgoing_queue.get()
            log.debug("Sending {}", cmd)
            connection.sendall(cmd.encode());
        except:
            log.error("Failed to send {}", cmd)

backend = Backend()
