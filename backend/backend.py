from streamcontroller_plugin_tools import BackendBase
from loguru import logger as log

import socket
import threading
import queue
import time
from dataclasses import dataclass

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

lock = threading.Lock()

@dataclass
class SocketThreadData:
    host: str = "127.0.0.1"
    port: int = 8080
    quit: bool = False

def socket_thread_run(data : SocketThreadData, outgoing_queue):
    log.debug("Connection thread start")
    connection = socket.socket()
    with lock:
        connection.connect((data.host, data.port))
    
    log.debug("Connection thread start - connected")
    while True:
        with lock:
            if data.quit == True:
                break

        connection.settimeout(0.001)
        received_data = None
        try:
            received_data = connection.recv(1024)
        except:
            pass
        
        if received_data:
            log.debug("Received data: {}", received_data)

        while not outgoing_queue.empty():
            try:
                cmd = outgoing_queue.get()
                log.debug("Sending {}", cmd)
                connection.sendall(cmd.encode());
            except:
                log.error("Failed to send {}", cmd)

        time.sleep(0.01) # 10 ms
    
    connection.close()
    log.debug("Connection thread stop")

class Backend(BackendBase):
    def __init__(self):
        super().__init__()

        self.thread_data = SocketThreadData()
        self.outgoing_queue = queue.Queue()

        self.socket_thread = threading.Thread(target=socket_thread_run, args=(self.thread_data, self.outgoing_queue,))
        self.socket_thread.start()

        self.threshold = 0

    def __del__(self):
        # TODO HOW?
        log.debug("on_disconnect 1")
        with lock:
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

backend = Backend()
