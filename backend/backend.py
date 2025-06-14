from loguru import logger as log

import socket
import threading
import queue
import time
from dataclasses import dataclass
from typing import Callable

import globals as gl

# To get access to plugin files
import sys
from pathlib import Path
ABSOLUTE_PLUGIN_PATH = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, ABSOLUTE_PLUGIN_PATH)

# TODO - Add ping to check if the socket is still connected?
# TODO - The 5 second wait on reconnect cause shutdown to take longer than it should

class Backend:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.stop_socket_thread = False
        self.outgoing_queue = queue.Queue()
        self.callbacks = []

        self.callbacks_mutex = threading.Lock()

        self.socket_thread = threading.Thread(target=self.socket_thread_run)
        self.socket_thread.start()

    def __del__(self):
        self.stop_socket_thread = True
        self.socket_thread.join()

    def set_port(self, port):
        self.port = port

    def inc_param(self, param_name, param_step):
        self.send_data(param_name + "|" + str(param_step))

    def dec_param(self, param_name, param_step):
        self.send_data(param_name + "|-" + str(param_step))

    def toggle_param(self, param_name):
        self.send_data(param_name + "!0")

    def request_param(self, param_name):
        self.send_data(param_name + "|0")

    def send_data(self, data):
        self.outgoing_queue.put(data)

    def add_callback(self, callback: Callable):
        with self.callbacks_mutex:
            if callback not in self.callbacks:
                log.debug("Adding callback: {}", callback)
                self.callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        with self.callbacks_mutex:
            if callback in self.callbacks:
                log.debug("Removing callback: {}", callback)
                self.callbacks.remove(callback)
            else:
                log.debug("Callback not found: {}", callback)

    def socket_thread_run(self):
        connection = None
        current_host = self.host
        current_port = self.port

        try:
            connection = self.socket_reconnect(connection, current_host, current_port)
        except Exception as e:
            log.error("Failed to connect to socket: {}", e)
        
        while True:
            if self.stop_socket_thread == True or gl.threads_running == False:
                break

            if not self.is_socket_connected(connection):
                log.error("Socket connection lost")
                try:
                    connection = self.socket_reconnect(connection, current_host, current_port)
                    time.sleep(0.1) # Wait a bit before trying to continue
                except Exception as e:
                    log.error("Failed to reconnect: {}", e)
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
        
        if connection is not None:
            connection.close()
        log.debug("Connection thread stop")

    def has_connection_parameters_changed(self, current_host, current_port):
        return self.host != current_host or self.port != current_port        
    
    def is_socket_connected(self, connection):
        if connection is None:
            return False
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

            with self.callbacks_mutex:
                if len(self.callbacks) > 0:
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
            cmd += "\n"  # Ensure the command ends with a newline
            connection.sendall(cmd.encode());
        except:
            log.error("Failed to send {}", cmd)
