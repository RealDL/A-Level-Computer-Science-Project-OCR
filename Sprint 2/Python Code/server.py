from _thread import *
from random import randint, choice
import string, math, socket
from Scripts.settings import Config
from Scripts.encryption import *
from Scripts.logger import *

logger.debug("RealDL Server Code.")

class Server(Config):
    def __init__(self):
        try:
            Config.__init__(self)
            self.initialize_server()
        except ValueError as Error:
            logger.error(f"Couldn't initialize server: {Error}") 

    def initialize_server(self):
        self.server = self.SERVER
        self.port = self.PORT
        self.players = {}
        self.connections = 0
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rsa_keys = RSA_Keys(self.ENCRYPTION_DATA_SIZE)
        self.public_key, self.private_key = self.rsa_keys.export_keys()
        self.rsa_encrypt = RSA_Encryption(self.public_key)

        try:
            self.s.bind((self.server, self.port))
        except socket.error as e:
            logger.error(f"Socket Error: {e}")
        self.s.listen()
        logger.info("Waiting for connections, Server Started")

    def create_random_string(self):
        characters = string.ascii_letters + string.digits
        return ''.join(choice(characters) for _ in range(self.ID_STRING_LENGTH))

    def is_touching(self, x, y, other_x, other_y, threshold):
        distance = math.sqrt((x + self.SQUARE_SIZE / 2 - other_x) ** 2 + (y + self.SQUARE_SIZE / 2 - other_y) ** 2)
        sum_half_widths = sum_half_heights = (self.SQUARE_SIZE + threshold) / 2
        return distance <= math.sqrt(sum_half_widths ** 2 + sum_half_heights ** 2)

    def get_player_position(self):
        x, y = randint(256, 763), randint(256, 634)
        while any(self.is_touching(x, y, p['x'], p['y'], self.SQUARE_SIZE) for p in self.players.values()):
            x, y = randint(256, 763), randint(256, 634)
        return x, y

    def create_new_player(self, username):
        key_string = self.create_random_string()
        player_x, player_y = self.get_player_position()
        return {
            "x": player_x,
            "y": player_y,
            "image": "Graphics/Game/player.png",
            "username": username,
            "id": key_string
        }, key_string

    def handle_client_communication(self, conn, key_string, aes_encryption):
        running = True
        while running:
            try:
                data = aes_encryption.decrypt(self.unserialize(conn.recv(self.DATA_SIZE)))
                self.players[key_string] = data
                logger.info(f"Received Player Dict: {data}.")

                if not data:
                    logger.info(f"Player {key_string} disconnected.")
                    running = False
                else:
                    reply = self.players
                    encrypted_reply = self.serialize(aes_encryption.encrypt(reply))

                conn.sendall(encrypted_reply)
                logger.info(f"Sending All Player Dict: {reply}.")
            except:
                logger.info(f"Player {key_string} lost connection.")
                running = False

        logger.info(f"Connection Closed for Player {key_string}.")
        del self.players[key_string]
        self.connections -= 1
        conn.close()

    def threaded_client(self, conn):
        try:
            # Send Public Key
            data_to_send = self.serialize(self.public_key)
            conn.send(data_to_send)
            logger.info(f"Sending Public Key: {self.public_key}")

            # Get AES Key and username
            dict_received_from_client = self.rsa_encrypt.decrypt(self.unserialize(conn.recv(self.ENCRYPTION_DATA_SIZE)),self.private_key)
            aes_key = dict_received_from_client['aes_key']
            username = dict_received_from_client['username']
            logger.info(f"Received AES Key: {aes_key}")

            # Create Player
            new_player, key_string = self.create_new_player(username)
            self.players[key_string] = new_player
            
            # Create AES Encryption and send player dict
            aes_encryption = AES_Encryption(aes_key)
            player_dict_send = {'player':new_player}
            encrypted_player = aes_encryption.encrypt(self.serialize(player_dict_send))
            conn.send(encrypted_player)
            logger.info(f"Sending Player dict to client: {new_player}")

            self.handle_client_communication(conn, key_string, aes_encryption)
        except:
            logger.error("An Error Occurred trying to setup Client-Server connection.")

    def run(self):
        while True:
            conn, addr = self.s.accept()
            self.connections += 1
            logger.info(f"Connected to: {addr}")
            logger.info(f"There are a total of {self.connections} connections!")

            start_new_thread(self.threaded_client, (conn,))

if __name__ == "__main__":
    server = Server()
    server.run()
