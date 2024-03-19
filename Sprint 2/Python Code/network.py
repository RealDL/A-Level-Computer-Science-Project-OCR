import socket
from Scripts.logger import *

logger.debug("RealDL Network Code.")

class Network():
    def __init__(self, server, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)
        
    def connect(self):
        try:
            self.client.connect(self.addr)
        except socket.error as Error:
            logger.error(f"Socket failed trying to connect: {Error}")

    def close(self):
        self.client.close()

    def receive(self, data_size):
        try:
            return self.client.recv(data_size)
        except socket.error as Error:
            logger.error(f"Socket failed trying to receive: {Error}")

    def send(self, data):
        try:
            self.client.send(data)
        except socket.error as Error:
            logger.error(f"Socket failed trying to send: {Error}")

    def sendall(self, data):
        try:
            self.client.sendall(data)
        except socket.error as Error:
            logger.error(f"Socket failed trying to sendall: {Error}")

