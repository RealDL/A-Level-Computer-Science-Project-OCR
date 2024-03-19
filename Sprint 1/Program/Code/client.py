import pygame, sys
from network import Network
from settings import Config
from level import Level
from player import Player
from logger import *
from encryption import *
from debug import debug

class Client(Config):
    def __init__(self):
        Config.__init__(self)
        pygame.init()
        self.initialize_pygame()
        self.initialize_network()

    def initialize_pygame(self):
        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Client")
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.run = True

    def initialize_network(self):
        # Setup Network
        self.network = Network()
        self.network.connect()

        # Get Public Key
        public_key_dict = self.unserialize(self.network.receive(self.ENCRYPTION_DATA_SIZE))
        self.public_key = self.unserialize(public_key_dict['public_key'])
        self.rsa_encrypt = RSA_Encryption(self.public_key)
        logger.info(f"Received Public Key: {self.public_key}")

        # Setup and send AES Encryption
        self.aes_key = AES_Keys(self.BITS)
        key = self.aes_key.export_key()
        key_dict = {'aes_key':key}
        encrypted_key_dict = self.serialize(self.rsa_encrypt.encrypt(key_dict))
        self.network.send(encrypted_key_dict)
        logger.info(f"Sending AES KEY: {key}")

        # Receive Player
        self.encryption = AES_Encryption(key)
        data = self.unserialize(self.encryption.decrypt(self.network.receive(self.ENCRYPTION_DATA_SIZE)))
        player_info = data['player']
        self.initialize_player(player_info)
        logger.info(f"Received player dict: {player_info}")

    def initialize_player(self, player_info):
        self.players = []
        self.player_x = player_info['x']
        self.player_y = player_info['y']
        self.player_image = player_info['image']
        self.id = player_info['id']
        self.player = Player([self.player_x, self.player_y], self.player_image, self.level.visible_sprites, self.level.obstacle_sprites, self.id)

    def update_players(self, player_dict):
        # Update existing player instances and remove players that are not in player_dict
        players_to_remove = []

        for player in self.players:
            if player.id in player_dict:
                player_data = player_dict[player.id]
                player.rect.x = player_data['x']
                player.rect.y = player_data['y']
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
                    player_data['id']
                )
                self.players.append(new_player)

    def redraw_window(self, all_players_dict):
        self.update_players(all_players_dict)
        self.win.fill(self.BG_COLOR)
        self.level.run(self.player)
        debug([self.player.rect.x, self.player.rect.y])
        pygame.display.update()
        self.clock.tick(self.FPS)

    def close(self):
        pygame.quit()
        sys.exit()

    def main(self):
        while self.run:
            player_dict = {'x': self.player.rect.x, 'y': self.player.rect.y, 'image': self.player_image, 'id': self.id}
            player_encrypted_dict = self.serialize(self.encryption.encrypt(player_dict))
            self.network.send(player_encrypted_dict)
            all_players_dict = self.encryption.decrypt(self.unserialize(self.network.receive(self.DATA_SIZE)))
            
            logger.debug("ALL DICT", all_players_dict)
            logger.debug("Sending player data:", player_dict)
            logger.debug("Received players dictionary:", all_players_dict)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.close()
            self.redraw_window(all_players_dict)

if __name__ == "__main__":
    client = Client()
    client.main()
