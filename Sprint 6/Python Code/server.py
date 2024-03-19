from Scripts.logger import *
try:
    from _thread import *
    from random import randint, choice
    import string, math, socket, time
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
        self.ready_to_play = False
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
        
        # Speed
        self.speed_leeway = 100
        self.allowed_speed = 10*(self.frame_increase_rate/1.55)
        # Health
        self.allowed_health = 300
        self.health_leeway = 15
        
        try:
            self.s.bind((self.server, self.port))
        except socket.error as e:
            logger.error(f"Socket Error: {e}")
        self.s.listen()
        logger.info("Waiting for connections, Server Started")
        logger.info(f"Server IP Address: {self.SERVER}")

    def create_random_string(self):
        characters = string.ascii_letters + string.digits
        return ''.join(choice(characters) for _ in range(self.ID_STRING_LENGTH))

    def is_touching(self, player_x, player_y, threshold=100):
        touching = False
        for player in self.players.values():
            # If two players are taking both an x and y position. We want to seperate player spawns.
            # The threshold is default at 100. We dont want players to close to each other.
            if abs(player['player']['x']-player_x) <= self.SQUARE_SIZE + threshold and abs(player['player']['y']-player_y) <= self.SQUARE_SIZE + threshold:
                touching = True
        return touching

    def get_player_position(self):
        def create_coords():
            random_area = choice(self.coordinates)
            if random_area == self.coordinates[2]:
                x = randint(random_area[0][0], random_area[1][0])
                y = randint(random_area[1][1], random_area[0][1])
            elif random_area == self.coordinates[5]:
                x = randint(random_area[1][0], random_area[0][0])
                y = randint(random_area[0][1], random_area[1][1])
            else:
                x = randint(random_area[0][0], random_area[1][0])
                y = randint(random_area[0][1], random_area[1][1])
            return x,y
        
        valid_coords = False
        while not valid_coords:
            x, y = create_coords()
            if not self.is_touching(x, y):
                valid_coords = True
        return x, y

    def validate_username(self, username):
        username_valid = False
        indent = 0
        usernames = [player['player']['username'] for player in self.players.values()]
        new_username = username
        while not username_valid:
            if indent > 0:
                new_username = username + f"_{str(indent)}"
            if new_username in usernames:
                indent += 1
            else:
                username_valid = True            
        return new_username

    def create_new_player(self, username):
        key_string = self.create_random_string()
        player_x, player_y = self.get_player_position()
        username = self.validate_username(username)
        return {
            "player":{
            "x": player_x,
            "y": player_y,
            "image": "Graphics/Game/player/down_idle/idle_down.png",
            "username": username,
            "status": "alive",
            "health": 100,
            "id": key_string,
            "kill_count":0,
            "killed_by":""
            },
            "weapon":[],
            "bullets":[],
            "magic":[]}, key_string

    def validate_movement(self, player_pos):
        def calculate_speed(pos1, pos2, delta_time):
            # Calculate distance between two positions using Euclidean distance formula
            try:
                delta_x = pos2[0] - pos1[0]
                delta_y = pos2[1] - pos1[1]
                distance = math.sqrt(delta_x**2 + delta_y**2)
                
                # Calculate speed (distance / time)
                speed = distance / delta_time
            except:
                speed = self.allowed_speed
            return speed
        
        # Calculate the distance moved between updates
        first_pos = player_pos[0][:2]
        last_pos = player_pos[-1][:2]
        total_time = sum(values[2] for values in player_pos)

        # Calculate speed between the first and last positions
        speed = calculate_speed(first_pos, last_pos, total_time)
        if speed > self.allowed_speed + self.speed_leeway:
            return False
        return True

    def validate_health(self, player):
        if player['health'] > self.allowed_health + self.health_leeway:
           return False
        else:
            return True
    
    def validate_player_status(self, player, data):
        if player['status'] == "dead" and data['status'] == 'alive':
            return player['status']
        elif player['status'] == "alive" and data['status'] == 'dead':
            return data['status']
        else:
            return player['status']
        
    def kill_count(self, key_string, kill_count, killed_players):
        kills = []

        # gets a list of all ids of players that have killed someone
        for player in self.players.values():
            if player['player']['killed_by'] != "":
                if player['player']['id'] not in killed_players:
                    kills.append(player['player']['killed_by'])
                    killed_players.append(player['player']['id'])
        
        # checks if this player has killed anyone
        for kill_id in kills:
            # #logger.debug(kill_count, kill_id, key_string)
            if kill_id == key_string:
                kill_count += 1
        return kill_count, killed_players

    def end_game(self):
        player_count = 0
        for player in self.players.values():
            if player['player']['status'] == "alive":
                player_count += 1
        if player_count <= 1:
            return True
        else:
            return False

    def validate_position(self, player):
        # Map boundaries, stops players from leaving the map.
        if player['x'] <= 180 or player['x'] >= 3400:
            return True
        elif player['y'] <= -50 or player['y'] >= 3150:
            return True
        else:
            return False

    def handle_client_communication(self, conn, key_string, aes_encryption):
        running = True
        player_pos = []
        killed_players = []
        last_time = time.time()
        end_time = 0
        reset_game_time = 15
        while running:
            try:
                ## ONE player left. -> after 30 seconds -> kick all players -> reset all key values

                # Recieve player data
                player_data = aes_encryption.decrypt(self.unserialize(conn.recv(self.DATA_SIZE)))

                # check the player's status is correct (this doesn't result in a kick)
                data = player_data['player']
                player_data['player']['status'] = self.validate_player_status(self.players[key_string]['player'], data)

                # Validate if the player has been killed.
                player_data['player']['kill_count'], killed_players = self.kill_count(key_string, player_data['player']['kill_count'], killed_players)

                self.players[key_string] = player_data

                if self.end_game():
                    if time.time() - end_time >= reset_game_time:
                        running = False
                else:
                    end_time = time.time()

                # Calculate the speed of play (FPS).
                delta_time = time.time() - last_time
                last_time = time.time()

                # Validate the player's position.
                if self.validate_position(self.players[key_string]['player']):
                    running = False
                    logger.info(f"Player {key_string} disconnected as they tried to leave the map.")


                # Validate the player data to ensure they are not speed hacking. (this does result in a kick)
                player_pos.append([self.players[key_string]['player']['x'], self.players[key_string]['player']['y'], delta_time])
                if len(player_pos) > 20: player_pos.pop(0)
                if not self.validate_movement(player_pos):
                    running = False
                    logger.info(f"Player {key_string} disconnected because they were speed hacking.")

                # Validiate player health to ensure they are not health hacking. (this does result in a kick)
                if not self.validate_health(self.players[key_string]['player']):
                    running = False
                    logger.info(f"Player {key_string} disconnected because they were health hacking.")

                #logger.info(f"Received Player Dict: {player_data}.")

                if not data:
                    logger.info(f"Player {key_string} disconnected.")
                    running = False
                else:
                    reply = self.players
                    encrypted_reply = self.serialize(aes_encryption.encrypt(reply))

                conn.sendall(encrypted_reply)
                #logger.info(f"Sending All Player Dict: {reply}.")
            except:
                logger.info(f"Player {key_string} lost connection.")
                running = False

        logger.info(f"Connection Closed for Player {key_string}.")
        try:
            del self.players[key_string]
            self.connections -= 1
        except:
            logger.info(f"No player with the ID: {key_string} exists.")
        conn.close()

    def waiting_zone(self, conn, key_string, aes_encryption):
        running = True
        while running:
            try:
                # send over number of players connected
                reply = {"connections":self.connections,"started":self.ready_to_play}
                encrypted_reply = self.serialize(aes_encryption.encrypt(reply))
    
                conn.sendall(encrypted_reply)
                # Receive start or not.
                start_dict = aes_encryption.decrypt(self.unserialize(conn.recv(self.DATA_SIZE)))
                start = start_dict["ready"]
                if start and self.connections >= 2:
                    self.ready_to_play = True
            except:
                running = False
                logger.error("Something went wrong.")

            if start:
                self.handle_client_communication(conn, key_string, aes_encryption)

        try:
            del self.players[key_string]
            self.connections -= 1
        except:
            logger.info(f"No player with the ID: {key_string} exists.")
        conn.close()


    def threaded_client(self, conn):
        try:
            # Send Public Key
            data_to_send = self.serialize(self.public_key)
            conn.send(data_to_send)
            #logger.info(f"Sending Public Key: {self.public_key}")

            # Get AES Key and username
            dict_received_from_client = self.rsa_encrypt.decrypt(self.unserialize(conn.recv(self.ENCRYPTION_DATA_SIZE)),self.private_key)
            aes_key = dict_received_from_client['aes_key']
            username = dict_received_from_client['username']
            aes_encryption = AES_Encryption(aes_key)
            #logger.info(f"Received AES Key: {aes_key} and Username: {username}")

            # Create Player
            new_player, key_string = self.create_new_player(username)
            self.players[key_string] = new_player
            #logger.info(f"Created New Player: {new_player}. ID: {key_string}")
            
            #Send player dict
            player_dict_send = {'player_data':new_player}
            encrypted_player = self.serialize(aes_encryption.encrypt(player_dict_send))
            conn.send(encrypted_player)
            logger.info(f"Sending Player dict to client: {new_player}")
            self.waiting_zone(conn, key_string, aes_encryption)
            #self.handle_client_communication(conn, key_string, aes_encryption)
        except:
            #logger.error("An Error Occurred trying to setup Client-Server connection.")
            try: 
                del self.players[key_string]
                self.connections -= 1
            except: 
                logger.info(f"No player was deleted.")
            conn.close()

    def run(self):
        while self.running:
            ## Limit on 5 players
            conn, addr = self.s.accept()
            logger.debug(f"Connections: {str(self.connections)}")
            
            if self.ready_to_play and self.connections == 0:
                self.ready_to_play = False

            if self.ready_to_play or self.connections >= 5:
                conn.close()
            else:
                self.connections += 1
            #logger.info(f"Connected to: {addr}")
            #logger.info(f"There {'is' if self.connections==1 else 'are'} {self.connections} {'client' if self.connections==1 else 'clients'} connected to the server!")

            start_new_thread(self.threaded_client, (conn,))

if __name__ == "__main__":
    try:
        server = Server()
        server.run()
    except:
        logger.critical("Server has failed to launch.")
