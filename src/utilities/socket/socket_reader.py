import logging
import os
import socket
import sys
import threading
import time

from queue import Queue


logger = logging.LoggerAdapter(logging.getLogger("sensiot"), {"class": os.path.basename(__file__)})

class SocketReader (threading.Thread):
    def __init__(self, name, event, queue, server_address="0.0.0.0", server_port=4711):
        threading.Thread.__init__(self)
        self.name = name
        self.event = event
        self.server_address = server_address
        self.server_port = server_port
        self.queue = queue
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)  # equals non-blocking
        logger.info("{} initialized successfully".format(self.name))

    def run(self):
        logger.info("Started {}".format(self.name))
        self.sock.bind((self.server_address, self.server_port))
        logger.info("Binded socket to {}:{}".format(self.server_address, str(self.server_port)))
        self.sock.listen(1)
        try:
            self.sock.makefile()
        except Exception as e:
            logger.error("{}".format(e))

        try:
            while not self.event.is_set():
                try:
                    logger.info('Waiting for incoming connections...')
                    connection, client_address = self.sock.accept()
                    if connection:
                        logger.info("Connection established")
                        logger.info("Start receiving data...")
                        message = b''
                        while not self.event.is_set():
                            chunk = connection.recv(1)
                            if not chunk or chunk == "\n".encode("utf-8"):
                                break
                            message += chunk
                        if message:
                            logger.info("Successfully received data")
                            decoded_message = str(message.decode("utf-8"))
                            self.queue.put(decoded_message)
                            logger.info("Data put into queue")
                        connection.close()
                except socket.timeout:
                    logger.info("Socket timed out...retrying")
                except Exception as e:
                    logger.error("Socket error: {}".format(e))
        finally:
            connection.close()
            logger.info("Stopped: {}".format(self.name))
