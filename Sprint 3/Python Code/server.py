from Scripts.logger import *
try:
    from _thread import *
    import random
    import string, math, socket
    from Scripts.settings import Config
    from Scripts.encryption import *
    from Scripts.debug import debug
except:
    logger.critical("You do not have all the modules installed. Please install Pygame, RSA and Pycryptodome.")

logger.debug("RealDL Server Code.")

class Server(Config):
    def __init__(self):
        try:
            Config.__init__(self)
            self.initialize_server()
        except:
            logger.error(f"Couldn't initialize server.") 

    def initialize_server(self):
        self.server = self.SERVER
        self.port = self.PORT
        self.players = {}
        self.connections = 0
        self.running = True
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rsa_keys = RSA_Keys(self.ENCRYPTION_DATA_SIZE)
        self.public_key, self.private_key = self.rsa_keys.export_keys()
        self.rsa_encrypt = RSA_Encryption(self.public_key)
        self.coordinates = [
            [[1030, 1270],[1278, 1616]],
            [[1100, 1660],[1278, 2180]],
            [[1420, 580],[2494, 432]],
            [[1670, 245],[1865, 592]],
            [[2250, 2485],[2622, 2896]],
            [[3134, 2485],[2818, 2832]]
            ]
        
        try:
            self.s.bind((self.server, self.port))
        except socket.error as e:
            logger.error(f"Socket Error: {e}")
        self.s.listen()
        logger.info("Waiting for connections, Server Started")
        logger.info(f"Server IP Address: {self.SERVER}")

    def create_random_string(self):
        try:
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(self.ID_STRING_LENGTH))
        except:
            logger.error("Failed to create unique string.")

    def is_touching(self, x, y, other_x, other_y, threshold):
        distance = math.sqrt((x + self.SQUARE_SIZE / 2 - other_x) ** 2 + (y + self.SQUARE_SIZE / 2 - other_y) ** 2)
        sum_half_widths = sum_half_heights = (self.SQUARE_SIZE + threshold) / 2
        return distance <= math.sqrt(sum_half_widths ** 2 + sum_half_heights ** 2)

    def get_player_position(self):
        def create_coords():
            random_area = random.choice(self.coordinates)
            if random_area == self.coordinates[2]:
                x = random.randint(random_area[0][0], random_area[1][0])
                y = random.randint(random_area[1][1], random_area[0][1])
            elif random_area == self.coordinates[5]:
                x = random.randint(random_area[1][0], random_area[0][0])
                y = random.randint(random_area[0][1], random_area[1][1])
            else:
                x = random.randint(random_area[0][0], random_area[1][0])
                y = random.randint(random_area[0][1], random_area[1][1])
            return x,y

        try:
            x, y = create_coords()
            while any(self.is_touching(x, y, p['x'], p['y'], self.SQUARE_SIZE) for p in self.players.values()):
                x, y = create_coords()
        except:
            x, y = create_coords()
        return x, y

    def username_validity(self, username):
        banned_words = [
            'assassin', 'bitch', 'dick', 'slutty', 'cunt', 'molester', 'crap', 'bully', 'cock','murder',
            'damn', 'arse', 'whore', 'penis', 'sex', 'glamour', 'murderer', 'rape', 'puppy', 'prick', 'hate',
            'bigot', 'mistress', 'kill', 'hella', 'smoke', 'tobacco', 'grass', 'nuclear', 'fart', 'soda',
            'loser', 'gory', 'tacky', 'weed', 'hoax', 'boss', 'meltdown', 'sin', 'public', 'furious', 'barf', 'dodo', 'labia',
            'hardcore', 'flirt', 'scary', 'pansy', 'rectum', 'noob', 'funky', 'banana', 'star', 'kinky', 'drug', 'gay', 'whiskey',
            'bite', 'dingo', 'gag', 'whip', 'sadist', 'car', 'mess', 'lick', 'trash', 'monster', 'hand', 'facist', 'sucker',
            'spank', 'porn','fuc','shit','nig']
        try:
            for word in banned_words:
                if word in username.lower():
                    return "Player"
            return username
        except:
            return username

    def create_new_player(self, username):
        key_string = self.create_random_string()
        player_x, player_y = self.get_player_position()
        username = self.username_validity(username)
        return {
            "x": player_x,
            "y": player_y,
            "image": "Graphics/Game/player/down_idle/idle_down.png",
            "username": username,
            "status": "alive",
            "health": 100,
            "id": key_string
        }, key_string

    def validate_movement(self, player_pos, player_data):
        # Calculate the distance moved between updates
        player_speed = 10
        leeway = 5
        average_player_distance = (player_speed*10) + leeway # Safety to ensure legit players have some leeway.
        delta_x = player_data['x'] - player_pos[0][0]
        delta_y = player_data['y'] - player_pos[0][1]
        distance_moved = math.sqrt(delta_x**2 + delta_y**2)
        

        if distance_moved > average_player_distance:
            return False
        return True

    def validate_health(self, player):
        leeyway = 5
        max_health = 300
        if player['health'] > max_health + leeyway:
           return max_health
        else:
            return player['health']
    
    def validate_player_status(self, player, data):
        if player['status'] == "dead" and data['status'] == 'alive':
            return player['status']
        else:
            return player['status']

    def handle_client_communication(self, conn, key_string, aes_encryption):
        running = True
        player_pos = []
        while running:
            try:
                # Receive data from player and check it is valid.
                data = aes_encryption.decrypt(self.unserialize(conn.recv(self.DATA_SIZE)))
                data['status'] = self.validate_player_status(self.players[key_string], data)
                self.players[key_string] = data

                # Validate the player data to ensure they are not hacking.
                player_pos.append([self.players[key_string]['x'], self.players[key_string]['y']])
                if len(player_pos) > 10: player_pos.pop(0)
                if not self.validate_movement(player_pos, self.players[key_string]):
                    running = False
                    logger.info(f"Player {key_string} disconnected because they were speed hacking.")
                self.players[key_string]['health'] = self.validate_health(self.players[key_string])
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
        try:
            del self.players[key_string]
        except:
            logger.info(f"No player with the ID: {key_string} exists.")
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
            logger.info(f"Received AES Key: {aes_key} and Username: {username}")
            aes_encryption = AES_Encryption(aes_key)

            # Create Player
            new_player, key_string = self.create_new_player(username)
            self.players[key_string] = new_player
            logger.info(f"Created New Player: {new_player}. ID: {key_string}")
            
            #Send player dict
            player_dict_send = {'player':new_player}
            encrypted_player = self.serialize(aes_encryption.encrypt(player_dict_send))
            conn.send(encrypted_player)
            logger.info(f"Sending Player dict to client: {new_player}")

            self.handle_client_communication(conn, key_string, aes_encryption)
        except:
            logger.error("An Error Occurred trying to setup Client-Server connection.")
            self.connections -= 1
            try: del self.players[key_string]
            except: logger.info(f"No player was deleted.")
            conn.close()

    def run(self):
        while self.running:
            conn, addr = self.s.accept()
            self.connections += 1
            logger.info(f"Connected to: {addr}")
            logger.info(f"There {'is' if self.connections==1 else 'are'} {self.connections} {'client' if self.connections==1 else 'clients'} connected to the server!")

            start_new_thread(self.threaded_client, (conn,))

if __name__ == "__main__":
    try:
        server = Server()
        server.run()
    except:
        logger.critical("Server has failed to launch.")
