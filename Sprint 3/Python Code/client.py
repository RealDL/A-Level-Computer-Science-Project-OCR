from Scripts.logger import *
try:
    import pygame, sys
    from Scripts.network import Network
    from Scripts.settings import Config
    from Scripts.level import Level
    from Scripts.player import Player
    from Scripts.encryption import *
    from Scripts.debug import debug
    from Scripts.functions import *
    from Scripts.ui import UI
    from Scripts.main_menu import MainMenu
except:
    logger.critical("You do not have all the modules installed. Please install Pygame, RSA and Pycryptodome.")

logger.info("RealDL - Client Code")
pygame.init()

class Client(Config):
    def __init__(self):
        try:
            Config.__init__(self)
            self.gameMenu = MainMenu()
        except:
            logger.error("Error, couldn't initalize the main menu.")
            self.close()

    def initialize_client(self, user_dict):
        logger.info("Client Connecting to Server")
        try:
            self.initialize_pygame(user_dict)
            self.initialize_network()
        except:
            logger.error("Error, couldn't initalize the client.")
            self.close()

    def initialize_pygame(self, user_dict):
        try:
            self.screen = self.gameMenu.screen # pygame.display.get_surface()
            self.clock = self.gameMenu.clock # pygame.time.Clock()
            self.custom_mouse = Mouse("Graphics/MainMenu/Mouse/mouse1.png", "Graphics/MainMenu/Mouse/mouse2.png", "Graphics/MainMenu/Mouse/mouse3.png")
            self.players = []
            self.player_count = len(self.players)
            self.kill_count = 0
            self.level = Level()
            self.ui = UI(self.custom_mouse, self.close, self.player_count, self.kill_count)
            self.running = True
            settings = user_dict['settings']
            start = user_dict['start']
            self.movement = settings['control']['movement']
            self.offense = settings['control']['offense']
            self.magic = settings['control']['magic']
            self.volume = settings['audio']['volume']
            self.sound = settings['audio']['sound']
            self.music = settings['audio']['music']
            self.username = start['username']
            self.server_ip = start['server_ip']
            self.SERVER = self.server_ip
        except:
            logger.error("Couldn't correctly initalize pygame.")
            self.close()

    def initialize_network(self):
        try:
            # Setup Network
            self.network = Network(self.SERVER, self.PORT)
            self.network.connect()

            # Get Public Key
            self.public_key = self.unserialize(self.network.receive(self.ENCRYPTION_DATA_SIZE))
            self.rsa_encrypt = RSA_Encryption(self.public_key)
            logger.info(f"Received Public Key: {self.public_key}")

            # Setup and send AES Encryption
            self.aes_key = AES_Keys(self.BITS)
            key = self.aes_key.export_key()
            dict_to_send_to_server = {'aes_key':key,'username':self.username}
            encrypted_key_dict = self.serialize(self.rsa_encrypt.encrypt(dict_to_send_to_server))
            self.network.send(encrypted_key_dict)
            logger.info(f"Sending AES KEY: {key}")

            # Receive Player
            self.encryption = AES_Encryption(key)
            data = self.encryption.decrypt(self.unserialize(self.network.receive(self.ENCRYPTION_DATA_SIZE)))
            player_info = data['player']
            self.initialize_player(player_info)
            logger.info(f"Received player dict: {player_info}")
        except:
            logger.error("Error. Failed to connect to that Server IP Address.")
            self.close()

    def initialize_player(self, player_info):
        self.player_x = player_info['x']
        self.player_y = player_info['y']
        self.player_image = player_info['image']
        self.username = player_info['username']
        self.id = player_info['id']
        self.status = player_info['status']
        self.health = player_info['health']
        self.player = Player([self.player_x, self.player_y], self.player_image, self.level.visible_sprites, self.level.obstacle_sprites, self.username, self.id, self.movement, self.offense, self.magic)

    def update_players(self, player_dict):
        # Update existing player instances and remove players that are not in player_dict
        try:
            players_to_remove = []

            for player in self.players:
                if player.id in player_dict:
                    player_data = player_dict[player.id]
                    player.rect.x = player_data['x']
                    player.rect.y = player_data['y']
                    try: player.image = pygame.image.load(player_data['image']).convert_alpha()
                    except: player.image = pygame.image.load(f"../{player_data['image']}").convert_alpha()
                else:
                    logger.debug(f"Removing player instance with id: {player.id}")
                    players_to_remove.append(player)

            for player in players_to_remove:
                self.players.remove(player)
                self.level.visible_sprites.remove(player)

            # Create new player instances for players not already in self.players
            for player_data in player_dict.values():
                player_ids = [player.id for player in self.players]
                if player_data['id'] not in player_ids:
                    logger.debug(f"Creating new player instance with id: {player_data['id']}")
                    new_player = Player(
                        [player_data['x'], player_data['y']],
                        player_data['image'],
                        self.level.visible_sprites,
                        self.level.obstacle_sprites,
                        player_data['username'],
                        player_data['id']
                    )
                    self.players.append(new_player)
        except:
            logger.error("Player disconected.")
            self.close()

    def redraw_window(self, all_players_dict):
        try:
            self.update_players(all_players_dict)
            self.level.run(self.player)
            self.ui.display(self.player)
            self.ui.draw_menu()
            debug(f"Position: ({self.player.rect.x}, {self.player.rect.y})",self.WIDTH/2, 20)
            if self.ui.draw_ui: self.player.paused = True
            else: self.player.paused = False
            pygame.display.update()
            self.clock.tick(self.FPS)
        except:
            logger.error("Player has left the game.")
            self.close()

    def close(self):
        try:
            self.network.close()
        except:
            logger.exception("No server-client connection.")
        self.running = False
        self.player = None
        self.players = None
        self.gameMenu.restart_menu()
        self.run()

    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()

    def main(self):
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.ui.draw_ui = not self.ui.draw_ui

                try:
                    # Get player data.
                    player_dict = {'x': self.player.rect.x, 
                                   'y': self.player.rect.y, 
                                   'image': self.player.get_image_name(), 
                                   'username':self.username, 
                                   'status':self.status, 
                                   'health':self.health,
                                   'id': self.id}
                    player_encrypted_dict = self.serialize(self.encryption.encrypt(player_dict))
                    self.network.send(player_encrypted_dict)
                    all_players_dict = self.encryption.decrypt(self.unserialize(self.network.receive(self.DATA_SIZE)))
                    
                    logger.debug(f"Players Dictionary: {all_players_dict}")
                    logger.debug(f"Sending player data: {player_dict}")
                    logger.debug(f"Received players dictionary: {all_players_dict}")

                    self.redraw_window(all_players_dict)
                except:
                    logger.error("Failed to send over player to server.")
                    self.close()
        except:
            logger.error("Failed to run main loop.")
            self.close()

    def run(self):
        self.gameMenu.run()
        user_dict = self.gameMenu.start_game()
        self.initialize_client(user_dict)
        self.main()

if __name__ == "__main__":
    try:
        client = Client()
        client.run()
    except:
        logger.error("Couldn't run main menu or client.")
