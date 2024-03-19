import socket
from settings import Config
from logger import *

logger.debug("RealDL Network Code.")

class Network(Config):
    def __init__(self):
        Config.__init__(self)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = self.SERVER
        self.port = self.PORT
        self.addr = (self.server, self.port)
        
    def connect(self):
        try:
            self.client.connect(self.addr)
        except socket.error as Error:
            logger.error(f"Socket failed trying to connect: {Error}")

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

