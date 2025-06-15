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

from enum import Enum

class SocketStates(Enum):
    INIT = 1
    CONNECTED = 2
    DISCONNECTED = 3
    RECONNECT_TIMEOUT = 4

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
        self.port = int(port)

    def set_host(self, host):
        self.host = host

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
                self.callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        with self.callbacks_mutex:
            if callback in self.callbacks:
                self.callbacks.remove(callback)
            else:
                log.error("Callback not found: {}", callback)

    def socket_thread_run(self):
        connection = None
        current_host = self.host
        current_port = self.port

        received_data = None

        state = SocketStates.INIT

        ping_interval_ns = 1000000000 # 1 second in nanoseconds
        last_ping_time = time.clock_gettime_ns(time.CLOCK_BOOTTIME)

        connection_interval_ns = 5000000000 # 5 seconds in nanoseconds
        last_connection_time = time.clock_gettime_ns(time.CLOCK_BOOTTIME)

        # Try first connection
        try:
            connection = self.socket_reconnect(connection, current_host, current_port)
            state = SocketStates.CONNECTED
        except Exception as e:
            log.error("Failed to connect to socket: {}", e)
            state = SocketStates.DISCONNECTED
        
        while True:
            current_time = time.clock_gettime_ns(time.CLOCK_BOOTTIME)

            # Check if the thread should stop
            if self.stop_socket_thread == True or gl.threads_running == False:
                break
            
            # Check if the connection parameters have changed
            if self.has_connection_parameters_changed(current_host, current_port):
                log.debug("Connection parameters changed")
                current_host = self.host
                current_port = self.port
                state = SocketStates.DISCONNECTED

            # Sleep for a short time to avoid busy waiting
            time.sleep(0.01)
            
            #
            # CONNECTED
            #
            if state == SocketStates.CONNECTED:

                #  - PING
                if current_time - last_ping_time > ping_interval_ns:
                    last_ping_time = current_time
                    if not self.send_ping(connection):
                        log.error("Ping failed, trying to reconnect")
                        state = SocketStates.DISCONNECTED

                #  - HANDLE DATA
                else:
                    # Receive data from the socket
                    try:
                        received_data = connection.recv(1024)
                        if received_data:
                            self.socket_thread_handle_message(received_data)
                    except:
                        pass

                    # Handle outgoing messages
                    while not self.outgoing_queue.empty():
                        if self.socket_thread_handle_outgoing(connection) is False:
                            log.error("Failed to send outgoing message, trying to reconnect")
                            state = SocketStates.DISCONNECTED

            #
            # DISCONNECTED
            #
            elif state == SocketStates.DISCONNECTED:
                try:
                    connection = self.socket_reconnect(connection, current_host, current_port)
                    state = SocketStates.CONNECTED
                except Exception as e:
                    last_connection_time = current_time
                    log.error("Failed to reconnect: {}", e)
                    state = SocketStates.RECONNECT_TIMEOUT

            #
            # WAIT FOR RECONNECT TRY
            #
            elif state == SocketStates.RECONNECT_TIMEOUT:
                # If reconnect faild, wait for a while before trying again
                if current_time - last_connection_time > connection_interval_ns:
                    state = SocketStates.DISCONNECTED
        
        if connection is not None:
            connection.close()
        log.debug("Connection thread stop")

    def has_connection_parameters_changed(self, current_host, current_port):
        return self.host != current_host or self.port != current_port        
    
    def send_ping(self, connection):
        if connection is None:
            return False
        try:
            # Try to send a small amount of data to check if the socket is still connected
            connection.sendall("ping".encode())
            return True
        except:
            return False
        
    def socket_reconnect(self, connection, host, port):
        log.debug("Reconnecting socket...")
        try:
            connection.close()
        except:
            pass
        connection = socket.socket()
        connection.settimeout(0.01) # Connection calls should not block
        connection.connect((host, port))
        log.debug("Socket connected to {}:{}", host, port)
        return connection
    
    # handle incoming messages
    def socket_thread_handle_message(self, received_data):
        for cmd in received_data.decode().split("\n"):
            cmd_strip = cmd.strip()
            if cmd_strip == "":
                continue

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
            cmd += "\n"  # Ensure the command ends with a newline
            connection.sendall(cmd.encode());
            return True
        except:
            log.error("Failed to send {}", cmd)
            return False
