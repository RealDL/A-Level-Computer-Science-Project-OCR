from Scripts.logger import *
try:
    import pygame, sys
    from Scripts.network import Network
    from Scripts.settings import Config
    from Scripts.level import Level
    from Scripts.player import Player
    from Scripts.weapon import *
    from Scripts.encryption import *
    from Scripts.debug import debug
    from Scripts.functions import *
    from Scripts.ui import UI
    from Scripts.main_menu import MainMenu
    from Scripts.magic import MagicPlayer
    from Scripts.particles import AnimationPlayer
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
            self.bullets = []
            self.weapons = []
            self.magic_animations = []
            self.player_count = len(self.players)
            self.kill_count = 0
            self.level = Level()
            # particles
            self.animation_player = AnimationPlayer()
            self.magic_player = MagicPlayer(self.animation_player)
            self.ui = UI(self.custom_mouse, self.close, self.player_count, self.kill_count)
            self.running = True

            # attack sprites
            self.current_attack = None
            self.bullet = None

            # User settings
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
            player_info = data['player_data']['player']
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
        self.player = Player([self.player_x, self.player_y], self.player_image, [self.level.visible_sprites], self.level.obstacle_sprites, self.username, self.id, self.health, self.create_attack, self.destroy_attack, self.create_bullet, self.create_magic, self.movement, self.offense, self.magic)
    
    def update_players(self, player_dict):
        # Update existing player instances and remove players that are not in player_dict
        try:
            ### Players ###

            # Update players
            players_to_remove = []
            for player in self.players:
                if player.id in player_dict:
                    player_data = player_dict[player.id]['player']
                    player.rect.x = player_data['x']
                    player.rect.y = player_data['y']
                    player.health = player_data['health']
                    try: player.image = pygame.image.load(player_data['image']).convert_alpha()
                    except: player.image = pygame.image.load(f"../{player_data['image']}").convert_alpha()
                else:
                    logger.debug(f"Removing player instance with id: {player.id}")
                    players_to_remove.append(player)

            # Delete players.
            for player in players_to_remove:
                self.players.remove(player)
                self.level.visible_sprites.remove(player)

            # Create new player instances for players not already in self.players
            for player_data in player_dict.values():
                player_info = player_data['player']
                player_ids = [player.id for player in self.players]
                if player_info['id'] not in player_ids:
                    logger.debug(f"Creating new player instance with ID: {player_info['id']}")
                    new_player = Player(
                        [player_info['x'], player_info['y']],
                        player_info['image'],
                        [self.level.visible_sprites],
                        self.level.obstacle_sprites,
                        player_info['username'],
                        player_info['id'],
                        player_info['health']
                    )
                    self.players.append(new_player)

            ### Weapons ###

            # Update Weapons
            weapons_to_remove = []
            for weapon in self.weapons:
                weapon_info = player_data['weapon']
                weapon_dict_ids = [weapon_dict['id'] for weapon_dict in weapon_info]
                weapon_dict_x = [weapon_dict['x'] for weapon_dict in weapon_info]
                weapon_dict_y = [weapon_dict['y'] for weapon_dict in weapon_info]
                weapon_dict_image = [weapon_dict['image'] for weapon_dict in weapon_info]
                if weapon.id in weapon_dict_ids:
                    weapon_index = weapon_dict_ids.index(weapon.id)
                    weapon.rect.x = weapon_dict_x[weapon_index]
                    weapon.rect.y = weapon_dict_y[weapon_index]
                    try: weapon.image = pygame.image.load(weapon_dict_image[weapon_index]).convert_alpha()
                    except: weapon.image = pygame.image.load(f"../{weapon_dict_image[weapon_index]}").convert_alpha()
                else:
                    logger.debug(f"Removing weapon instance with id: {weapon.id}")
                    weapons_to_remove.append(weapon)

            # Delete weapons.
            for weapon in weapons_to_remove:
                self.weapons.remove(weapon)
                self.level.visible_sprites.remove(weapon)

            # Create weapons
            for player_data in player_dict.values():
                weapon_info = player_data['weapon']
                weapon_ids = [weapon.id for weapon in self.weapons]
                weapon_dict_ids = [weapon_dict['id'] for weapon_dict in weapon_info]
                for weapon_id, weapon_data in zip(weapon_dict_ids, weapon_info):
                    if weapon_id not in weapon_ids:
                        logger.debug(f"Creating a new weapon with the ID: {weapon_data['id']}")
                        new_weapon = Weapon([self.level.visible_sprites],
                                            weapon_data['x'],
                                            weapon_data['y'],
                                            weapon_data['id'],
                                            weapon_data['image'])
                        self.weapons.append(new_weapon)

            ### Bullets ###

            # Update Bullets
            bullets_to_remove = []
            for bullet in self.bullets:
                bullet_info = player_data['bullets']
                bullet_dict_ids = [bullet_dict['id'] for bullet_dict in bullet_info]
                bullet_dict_x = [bullet_dict['x'] for bullet_dict in bullet_info]
                bullet_dict_y = [bullet_dict['y'] for bullet_dict in bullet_info]
                bullet_dict_image = [bullet_dict['image'] for bullet_dict in bullet_info]
                if bullet.id in bullet_dict_ids:
                    bullet_index = bullet_dict_ids.index(bullet.id)
                    bullet.rect.x = bullet_dict_x[bullet_index]
                    bullet.rect.y = bullet_dict_y[bullet_index]
                    try: bullet.image = pygame.image.load(bullet_dict_image[bullet_index]).convert_alpha()
                    except: bullet.image = pygame.image.load(f"../{bullet_dict_image[bullet_index]}").convert_alpha()
                else:
                    logger.debug(f"Removing bullet instance with id: {bullet.id}")
                    bullets_to_remove.append(bullet)

            # Delete Bullets
            for bullet in bullets_to_remove:
                self.bullets.remove(bullet)
                self.level.visible_sprites.remove(bullet)

            # Create Bullets
            for player_data in player_dict.values():
                bullet_info = player_data['bullets']
                bullet_ids = [bullet.id for bullet in self.bullets]
                bullet_dict_ids = [bullet_dict['id'] for bullet_dict in bullet_info]
                for bullet_id, bullet_data in zip(bullet_dict_ids, bullet_info):
                    if bullet_id not in bullet_ids:
                        logger.debug(f"Creating a new weapon with the ID: {bullet_data['id']}")
                        new_bullet = Weapon([self.level.visible_sprites],
                                            bullet_data['x'],
                                            bullet_data['y'],
                                            bullet_data['id'],
                                            bullet_data['image'],
                                            "bullet_copy")
                        self.bullets.append(new_bullet)

            ### Magic ###

            # Update Magic Animation

            magic_to_remove = []
            for magic in self.magic_animations:
                magic_info = player_data['magic']
                magic_dict_ids = [magic_dict['id'] for magic_dict in magic_info]
                magic_dict_x = [magic_dict['x'] for magic_dict in magic_info]
                magic_dict_y = [magic_dict['y'] for magic_dict in magic_info]
                magic_dict_image = [magic_dict['image'] for magic_dict in magic_info]
                if magic.id in magic_dict_ids:
                    magic_index = magic_dict_ids.index(magic.id)
                    magic.rect.x = magic_dict_x[magic_index]
                    magic.rect.y = magic_dict_y[magic_index]
                    try: magic.image = pygame.image.load(magic_dict_image[magic_index]).convert_alpha()
                    except: magic.image = pygame.image.load(f"../{magic_dict_image[magic_index]}").convert_alpha()
                else:
                    logger.debug(f"Removing bullet instance with id: {magic.id}")
                    magic_to_remove.append(magic)
                    
            # Delete Bullets
            for magic in magic_to_remove:
                self.magic_animations.remove(magic)
                self.level.visible_sprites.remove(magic)

            # Create Magic Animation
            for player_data in player_dict.values():
                magic_info = player_data['magic'] 
                magic_ids = [magic.id for magic in self.magic_animations]
                magic_dict_ids = [magic_dict['id'] for magic_dict in magic_info]
                for magic_id, magic_data in zip(magic_dict_ids, magic_info):
                    if magic_id not in magic_ids:
                        logger.debug(f"Creating a new Magic Animation with the ID: {magic_data['id']}")
                        new_magic_animation = Weapon([self.level.visible_sprites],
                                                magic_data['x'],
                                                magic_data['y'],
                                                magic_data['id'],
                                                magic_data['image'],
                                                "magic_copy")
                        self.magic_animations.append(new_magic_animation)


        except:
            logger.error("Player disconected.")
            self.close()

    def redraw_window(self, all_players_dict):
        try:
            self.update_players(all_players_dict)
            self.level.run(self.player)
            self.ui.display(self.player)
            debug(f"Position: ({self.player.rect.x}, {self.player.rect.y})",self.WIDTH/2, 20)
            self.ui.draw_menu()
            if self.ui.draw_ui: self.player.paused = True
            else: self.player.paused = False
            pygame.display.update()
            self.clock.tick(self.FPS)
        except:
            logger.error("Player has left the game.")
            self.close()

    def create_attack(self):
        logger.info("Create attack")
        try:
            self.current_attack = Melee(self.player, [self.level.visible_sprites,self.level.attack_sprites])
        except:
            self.current_attack = None
            logger.error("Failed to render attack image.")

    def create_bullet(self):
        logger.info("Bullet!")
        self.bullet = Bullets(self.player, [self.level.visible_sprites, self.level.attack_sprites], self.level.obstacle_sprites)

    def destroy_attack(self):
        logger.info("destroy attack.")
        try:
            if self.current_attack:
                self.current_attack.kill()
            self.current_attack = None
        except:
            self.current_attack = None
            logger.error("Failed to destroy attack.")

    def create_magic(self,style,strength,cost):
        if style == 'heal':
            self.magic_player.heal(self.player,strength,cost,[self.level.visible_sprites])

        if style == 'flame':
            self.magic_player.flame(self.player,cost,[self.level.visible_sprites,self.level.attack_sprites])

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

    def return_weapon(self):
        weapon = []
        for sprite in self.level.visible_sprites:
            if sprite.sprite_type == "weapon":
                weapon_dict = {"x":sprite.rect.x,"y":sprite.rect.y,"image":sprite.full_path,"id":sprite.id}
                weapon.append(weapon_dict)
        
        return weapon
    
    def return_bullets(self):
        bullets = []

        for sprite in self.level.visible_sprites:
            if sprite.sprite_type == "bullet":
                bullet_dict = {"x":sprite.rect.x,
                               "y":sprite.rect.y,
                                "image":sprite.full_path,
                                "id":sprite.id}
                bullets.append(bullet_dict)
        return bullets

    def return_magic_data(self):
        magic = []
        for sprite in self.level.visible_sprites:
            if sprite.sprite_type == "magic":
                magic_dict = {"x":sprite.rect.x,
                              "y":sprite.rect.y,
                              "image":sprite.return_image(),
                              "id":sprite.id}
                magic.append(magic_dict)
        return magic

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
                    # Get player data
                    player_dict = {'x': self.player.rect.x, 
                                   'y': self.player.rect.y, 
                                   'image': self.player.get_image_name(), 
                                   'username':self.username, 
                                   'status':self.status, 
                                   'health':self.player.health,
                                   'id': self.id}
                    player_total_dict = {'player':player_dict,'weapon':self.return_weapon(),'bullets':self.return_bullets(),'magic':self.return_magic_data()}
                    player_encrypted_dict = self.serialize(self.encryption.encrypt(player_total_dict))
                    self.network.send(player_encrypted_dict)
                    all_players_dict = self.encryption.decrypt(self.unserialize(self.network.receive(self.DATA_SIZE)))

                    logger.debug(f"Sending player data: {player_total_dict}")
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
