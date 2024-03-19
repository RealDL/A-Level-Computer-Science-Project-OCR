from Scripts.logger import *
try:
    import pygame, sys, time
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
            self.join_game = False
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

            # Sound and Music
            try:
                self.sword_sound = pygame.mixer.Sound("Audio/sword.wav")
                self.damage_sound = pygame.mixer.Sound("Audio/hit.wav")
                self.heal_sound = pygame.mixer.Sound("Audio/heal.wav")
                self.fire_sound = pygame.mixer.Sound("Audio/Fire.wav")
                self.death_sound = pygame.mixer.Sound("Audio/death.wav")
                self.background_music = pygame.mixer.Sound("Audio/main.ogg")
            except:
                self.sword_sound = pygame.mixer.Sound("../Audio/sword.wav")
                self.damage_sound = pygame.mixer.Sound("../Audio/hit.wav")
                self.heal_sound = pygame.mixer.Sound("../Audio/heal.wav")
                self.fire_sound = pygame.mixer.Sound("../Audio/Fire.wav")
                self.death_sound = pygame.mixer.Sound("../Audio/death.wav")
                self.background_music = pygame.mixer.Sound("../Audio/main.ogg")
            
            # particles
            self.animation_player = AnimationPlayer()
            self.magic_player = MagicPlayer(self.animation_player)
            self.ui = UI(self.custom_mouse, self.close, self.player_count, self.kill_count)
            self.running = True

            # attack sprites
            self.current_attack = None
            self.bullet = None
            self.attacked_sprites_ids = []

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
            self.previous_time = 0
            self.dt = 0
            
            # Game Over
            self.game_over = Text(self.gameMenu.text_height, "Graphics/Fonts/Orbitron-ExtraBold.ttf",(247,155,16), None, None, None, self.gameMenu.base_text_size*10)
            self.game_over_board = Button((27,31,35), (27,31,35), self.gameMenu.settings.WIDTH/2, self.gameMenu.settings.HEIGHT/2*0.4, "Graphics/Fonts/Orbitron-Regular.ttf", (27,31,35), (27,31,35), self.gameMenu.settings.WIDTH*0.55, self.gameMenu.settings.HEIGHT*0.2,'','Rectangle', None, self.gameMenu.big_text_size, int(self.gameMenu.curve*1.5))
            
            # Leaderboard
            self.leaderboard = Button((27,31,35), (27,31,35), self.gameMenu.settings.WIDTH/2*1.78, self.gameMenu.settings.HEIGHT/2, "Graphics/Fonts/Orbitron-Regular.ttf", (27,31,35), (27,31,35), self.gameMenu.settings.WIDTH*0.2, self.gameMenu.settings.HEIGHT*0.7,'','Rectangle', None, self.gameMenu.big_text_size, int(self.gameMenu.curve*1.5))
            self.leaderboard_text = Text(self.gameMenu.text_height, "Graphics/Fonts/Orbitron-Bold.ttf",(240,240,240), None, None, None, self.gameMenu.base_text_size*3)
            self.leaderboard2 = Button((27,31,35), (27,31,35), self.gameMenu.settings.WIDTH/2*1.78, self.gameMenu.settings.HEIGHT/2*1.06, "Graphics/Fonts/Orbitron-Regular.ttf", (27,31,35), (27,31,35), self.gameMenu.settings.WIDTH*0.18, self.gameMenu.settings.HEIGHT*0.6,'','Rectangle', None, self.gameMenu.big_text_size, int(self.gameMenu.curve*1.5))
            self.value_board = Text(self.gameMenu.text_height, "Graphics/Fonts/Orbitron-Medium.ttf",(240,240,240), None, None, None, self.gameMenu.base_text_size*3)

            self.game_finished = False
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
        self.kill_count = player_info['kill_count']
        self.killed_by = player_info['killed_by']
        self.player = Player([self.player_x, self.player_y], self.player_image, [self.level.visible_sprites], self.level.obstacle_sprites, self.username, self.id, self.health, self.create_attack, self.destroy_attack, self.create_bullet, self.create_magic, self.movement, self.offense, self.magic, self.status)
    
    def update_players(self, player_dict, dictionary_copy):
        # Update existing player instances and remove players that are not in player_dict
        try:
            ### Player Sounds ###

            for player_data, old_player_data in zip(player_dict.values(), dictionary_copy.values()):
                player_info = player_data['player']
                old_player_info = old_player_data['player']

                if player_info['id'] != self.player.id:
                    ### Player Got Hit ###
                    if player_info['health'] < old_player_info['health']:
                        if self.sound == 1:
                            self.damage_sound.play()
                
                    ### Player dies ###
                    if player_info['status'] == "dead" and old_player_info['status'] == "alive":
                        if self.sound == 1:
                            self.death_sound.play()

                    ### Weapons ###
                    weapon_ids = [weapon['player_id'] for weapon in player_data['weapon']]
                    weapon_type = [weapon['type'] for weapon in player_data['weapon']]
                    old_weapon_ids = [old_weapon['player_id'] for old_weapon in old_player_data['weapon']]
                    new_weapon_ids = set(weapon_ids) - set(old_weapon_ids)
                    if new_weapon_ids:
                        for new_weapon_id in new_weapon_ids:
                            weapon_index = weapon_ids.index(new_weapon_id)
                            animation_type = weapon_type[weapon_index]
                            if self.sound == 1:
                                if animation_type == "melee":
                                    self.sword_sound.play()
                    
                    ### Bullets ###
                    bullet_ids = [bullet['id'] for bullet in player_data['bullets']]
                    old_bullet_ids = [old_bullet['id'] for old_bullet in old_player_data['bullets']]
                    new_bullet_ids = set(bullet_ids) - set(old_bullet_ids)
                    if new_bullet_ids:
                        for new_bullet_id in new_bullet_ids:
                            if self.sound == 1:
                                self.sword_sound.play()

                    ### Fire Animation ###
                    magic_ids = [magic['player_id'] for magic in player_data['magic']]
                    magic_type = [magic['type'] for magic in player_data['magic']]
                    old_magic_ids = [old_magic['player_id'] for old_magic in old_player_data['magic']]
                    new_magic_ids = set(magic_ids) - set(old_magic_ids)
                    if new_magic_ids:
                        for new_magic_id in new_magic_ids:
                            magic_index = magic_ids.index(new_magic_id)
                            animation_type = magic_type[magic_index]
                            if self.sound == 1:
                                if animation_type == "flame":
                                    self.fire_sound.play()
                                if animation_type == "aura":
                                    self.heal_sound.play()
                

            ### Players ###
                            
            existing_player_ids = [player.id for player in self.players]
            players_to_remove = []

            for player_data in player_dict.values():
                player_info = player_data['player']
                player_id = player_info['id']

                if player_id == self.player.id and self.kill_count < player_info['kill_count']:
                    self.player.exp += 1000
                    self.kill_count = player_info['kill_count']
                    self.player.kill_count = player_info['kill_count']

                if player_id in existing_player_ids:
                    # Update existing players
                    for player in self.players:
                        if player.id == player_id:
                            player.kill_count = player_info['kill_count']
                            player.rect.x = player_info['x']
                            player.rect.y = player_info['y']
                            player.health = player_info['health']
                            player.status_alive = player_info['status']
                            try: player.image = pygame.image.load(player_info['image']).convert_alpha()
                            except: player.image = pygame.image.load(f"../{player_info['image']}").convert_alpha()
                            
                else:
                    #logger.debug(f"Creating new player instance with ID: {player_id}")
                    new_player = Player(
                        [player_info['x'], player_info['y']],
                        player_info['image'],
                        [self.level.visible_sprites, self.level.player_sprites],
                        self.level.obstacle_sprites,
                        player_info['username'],
                        player_id,
                        player_info['health']
                    )
                    self.players.append(new_player)

            # Remove players not found in player_dict
            for player in self.players:
                if player.id not in player_dict:
                    #logger.debug(f"Removing player instance with id: {player.id}")
                    players_to_remove.append(player)

            for player in players_to_remove:
                self.players.remove(player)
                self.level.visible_sprites.remove(player)
                player.kill()

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
                    #logger.debug(f"Removing weapon instance with id: {weapon.id}")
                    weapons_to_remove.append(weapon)

            # Delete weapons.
            for weapon in weapons_to_remove:
                self.weapons.remove(weapon)
                self.level.visible_sprites.remove(weapon)
                weapon.kill()

            # Create weapons
            for player_data in player_dict.values():
                weapon_info = player_data['weapon']
                weapon_ids = [weapon.id for weapon in self.weapons]
                weapon_dict_ids = [weapon_dict['id'] for weapon_dict in weapon_info]
                for weapon_id, weapon_data in zip(weapon_dict_ids, weapon_info):
                    if weapon_id not in weapon_ids:
                        #logger.debug(f"Creating a new weapon with the ID: {weapon_data['id']}")
                        new_weapon = Weapon([self.level.visible_sprites, self.level.attack_sprites],
                                            weapon_data['x'],
                                            weapon_data['y'],
                                            weapon_data['id'],
                                            weapon_data['image'],
                                            weapon_data['player_id'],
                                            weapon_data['damage'])
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
                    #logger.debug(f"Removing bullet instance with id: {bullet.id}")
                    bullets_to_remove.append(bullet)

            # Delete Bullets
            for bullet in bullets_to_remove:
                self.bullets.remove(bullet)
                self.level.visible_sprites.remove(bullet)
                bullet.kill()

            # Create Bullets
            for player_data in player_dict.values():
                bullet_info = player_data['bullets']
                bullet_ids = [bullet.id for bullet in self.bullets]
                bullet_dict_ids = [bullet_dict['id'] for bullet_dict in bullet_info]
                for bullet_id, bullet_data in zip(bullet_dict_ids, bullet_info):
                    if bullet_id not in bullet_ids:
                        #logger.debug(f"Creating a new weapon with the ID: {bullet_data['id']}")
                        new_bullet = Weapon([self.level.visible_sprites, self.level.attack_sprites],
                                            bullet_data['x'],
                                            bullet_data['y'],
                                            bullet_data['id'],
                                            bullet_data['image'],
                                            bullet_data['player_id'],
                                            bullet_data['damage'],
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
                    magic.full_path = magic_dict_image[magic_index]

                    try: magic.image = pygame.image.load(magic.full_path).convert_alpha()
                    except: magic.image = pygame.image.load(f"../{magic.full_path}").convert_alpha()
                    
                else:
                    #logger.debug(f"Removing magic instance with id: {magic.id}")
                    magic_to_remove.append(magic)
                    
            # Delete Magic
            for magic in magic_to_remove:
                self.magic_animations.remove(magic)
                self.level.visible_sprites.remove(magic)
                magic.kill()

            # Create Magic Animation
            for player_data in player_dict.values():
                magic_info = player_data['magic'] 
                magic_ids = [magic.id for magic in self.magic_animations]
                magic_dict_ids = [magic_dict['id'] for magic_dict in magic_info]
                for magic_id, magic_data in zip(magic_dict_ids, magic_info):
                    if magic_id not in magic_ids:
                        #logger.debug(f"Creating a new Magic Animation with the ID: {magic_data['id']}")
                        if magic_data['type'] == "flame":
                            new_magic_animation = Weapon([self.level.visible_sprites, self.level.attack_sprites],
                                                    magic_data['x'],
                                                    magic_data['y'],
                                                    magic_data['id'],
                                                    magic_data['image'],
                                                    magic_data['player_id'],
                                                    magic_data['damage'],
                                                    "magic_copy")
                        else:
                            new_magic_animation = Weapon([self.level.visible_sprites],
                                                    magic_data['x'],
                                                    magic_data['y'],
                                                    magic_data['id'],
                                                    magic_data['image'],
                                                    magic_data['player_id'],
                                                    None,
                                                    "magic_copy")
                        self.magic_animations.append(new_magic_animation)


        except:
            logger.error("Player disconected.")
            self.close()

    def players_number(self):
        player_count = 0
        player_list = [player.status_alive for player in self.players]
        for status in player_list:
            if status == "alive":
                player_count += 1
        return player_count
    
    def redraw_window(self, all_players_dict, dictionary_copy):
        try:
            self.update_players(all_players_dict, dictionary_copy) # could be this
            self.level.run(self.player, self.dt)
            """self.player_attack_logic() # could be this"""
            self.player_attack_collisions()
            self.ui.player_count = self.players_number()
            self.ui.player_kill_count = self.kill_count
            self.ui.display(self.player)
            self.one_player_remaining()

            debug(f"Position: ({self.player.rect.x}, {self.player.rect.y})",self.WIDTH/2, 20)
            if self.dt != 0: debug(f"FPS: {int(1/self.dt)}",self.WIDTH/2, 50)
            debug(f"{self.player.direction}",self.WIDTH/2, 80)
            self.ui.draw_menu()
            if self.ui.draw_ui: self.player.paused = True
            else: self.player.paused = False
            pygame.display.update()
            # self.clock.tick(5)
        except:
            logger.error("Player has left the game.")
            self.close()

    def create_attack(self, weapon_type="melee"):
        #logger.info("Create attack")
        try:
            if self.sound == 1 and weapon_type == "melee":
                self.sword_sound.play()
            self.current_attack = Melee(self.player, [self.level.visible_sprites], self.player.id)
        except:
            self.current_attack = None
            #logger.error("Failed to render attack image.")

    def create_bullet(self):
        #logger.info("Bullet!")
        if self.sound == 1:
            self.sword_sound.play()
        self.bullet = Bullets(self.player, [self.level.visible_sprites], self.level.obstacle_sprites, self.player.id, self.level.player_sprites)

    def destroy_attack(self):
        #logger.info("destroy attack.")
        try:
            if self.current_attack:
                self.current_attack.kill()
            self.current_attack = None
        except:
            self.current_attack = None
            #logger.error("Failed to destroy attack.")

    def create_magic(self,style,strength,cost):
        if style == 'heal':
            if self.sound == 1 and self.player.energy > cost:
                self.heal_sound.play()
            self.magic_player.heal(self.player,strength,cost,[self.level.visible_sprites], self.player.id)

        if style == 'flame':
            if self.sound == 1 and self.player.energy > cost:
                self.fire_sound.play()
            self.magic_player.flame(self.player,strength,cost,[self.level.visible_sprites], self.player.id)

    def close(self):
        try:
            self.network.close()
        except:
            logger.exception("No server-client connection.")
        self.background_music.stop()
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
                weapon_dict = {"x":sprite.rect.x,
                               "y":sprite.rect.y,
                               "image":sprite.full_path,
                               "damage":sprite.damage,
                               "type":sprite.type,
                               "id":sprite.id,
                               "player_id":self.player.id}
                weapon.append(weapon_dict)
        return weapon
    
    def return_bullets(self):
        bullets = []

        for sprite in self.level.visible_sprites:
            if sprite.sprite_type == "bullet":
                bullet_dict = {"x":sprite.rect.x,
                               "y":sprite.rect.y,
                                "image":sprite.full_path,
                                "damage":sprite.damage,
                                "id":sprite.id,
                                "player_id":self.player.id}
                bullets.append(bullet_dict)
        return bullets

    def return_magic_data(self):
        magic = []
        for sprite in self.level.visible_sprites:
            if sprite.sprite_type == "magic":
                magic_dict = {"x":sprite.rect.x,
                              "y":sprite.rect.y,
                              "image":sprite.return_image(),
                              "type":sprite.return_type(),
                              "damage":sprite.return_strength(),
                              "id":sprite.id,
                              "player_id":self.player.id}
                magic.append(magic_dict)
        return magic

    def player_attack_collisions(self):
        # Removes attack sprite id that are no longer in the game
        sprite_ids = [sprite.id for sprite in self.level.visible_sprites]
        for sprite_id in self.attacked_sprites_ids:
            if sprite_id not in sprite_ids:
                self.attacked_sprites_ids.remove(sprite_id)

        if self.level.attack_sprites:
            for attack_sprite in self.level.attack_sprites:
                if "copy" in attack_sprite.sprite_type:
                    # Checks if the attack is not from our player
                    if attack_sprite.player_id != self.player.id:
                        player_collisions = pygame.sprite.spritecollide(attack_sprite,self.level.player_sprites,False)
                        if player_collisions:
                            for player in player_collisions:
                                if attack_sprite.damaged_player != True and attack_sprite.id not in self.attacked_sprites_ids:
                                    if player.id == self.player.id and self.player.health > 0:
                                        self.attacked_sprites_ids.append(attack_sprite.id)
                                        attack_sprite.damaged_player = True
                                        old_player_health = self.player.health
                                        if self.sound == 1:
                                            self.damage_sound.play()
                                        self.player.damage_player(attack_sprite.damage)
                                        if self.player.health == 0 and old_player_health > 0 and self.killed_by == '':
                                            if self.sound == 1:
                                                self.death_sound.play()
                                            self.killed_by = attack_sprite.player_id
                                        if "bullet" in attack_sprite.sprite_type:
                                            attack_sprite.kill()
                                            
    def main(self):
        dictionary_copy = {}
        self.background_music.play(-1)
        if self.music == 1:
            self.background_music.set_volume(self.volume/100)
        else:
            self.background_music.set_volume(0)
        try:
            self.previous_time = time.time()
            while self.running:
                current_time = time.time()
                self.dt = current_time - self.previous_time
                self.previous_time = current_time

                self.handle_events()

                try:
                    all_players_dict = self.send_player_data()
                    
                    #logger.debug(f"Sending player data: {all_players_dict}")
                    #logger.debug(f"Received players dictionary: {all_players_dict}")
                    self.redraw_window(all_players_dict, dictionary_copy)
                    dictionary_copy = all_players_dict
                except Exception as e:
                    logger.error(f"Failed to send/receive player data: {e}")
                    self.close()

        except Exception as e:
            logger.error(f"Failed to run main loop: {e}")
            self.close()

    def one_player_remaining(self):
        if self.players_number() == 1 or self.game_finished:
            ## Player has won.
            self.game_finished = True
            
            ## Animation
            self.game_over_board.draw((27,31,35), None, None, True, None, None, None, "draw")
            self.game_over.draw("draw", "Game Over!",(self.gameMenu.settings.WIDTH/2), (self.gameMenu.settings.HEIGHT/2*0.4))
            
            ## Display kill counts for all players
            self.leaderboard.draw((27,31,35))           
            self.leaderboard2.draw((240,240,240))
            self.leaderboard_text.draw("draw", "Leaderboard",(self.gameMenu.settings.WIDTH/2*1.78), (self.gameMenu.settings.HEIGHT/2*0.375))
            leaderboard_text = "\n".join([f"{player.username}: {player.kill_count}" for player in sorted(self.players, key=lambda x: x.kill_count, reverse=True)])
            leaderboard_list = leaderboard_text.split('\n')
            for index, leaderboard_index in enumerate(leaderboard_list):
                spacing_index = 0.52 + 0.1*index
                self.value_board.draw("draw",leaderboard_index,(self.gameMenu.settings.WIDTH/2*1.78), (self.gameMenu.settings.HEIGHT/2*spacing_index))

            ## Reset key player data
            ## Log out after a 30 second.
        else:
            self.game_over.draw("undraw", "Game Over!",(self.gameMenu.settings.WIDTH/2), (self.gameMenu.settings.HEIGHT/2*0.4))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.ui.draw_ui = not self.ui.draw_ui
    
    def send_player_data(self):
        player_dict = {
            'x': self.player.rect.x,
            'y': self.player.rect.y,
            'image': self.player.get_image_name(),
            'username': self.username,
            'status': self.player.return_alive_status(),
            'health': self.player.health,
            'id': self.id,
            'kill_count': self.kill_count,
            'killed_by': self.killed_by
        }
        player_total_dict = {
            'player': player_dict,
            'weapon': self.return_weapon(),
            'bullets': self.return_bullets(),
            'magic': self.return_magic_data()
        }
        player_encrypted_dict = self.serialize(self.encryption.encrypt(player_total_dict))
        self.network.send(player_encrypted_dict)
        all_players_dict = self.encryption.decrypt(self.unserialize(self.network.receive(self.DATA_SIZE)))
        return all_players_dict

    def run(self):
        self.join_game = False
        self.gameMenu.run()
        user_dict = self.gameMenu.start_game()
        self.initialize_client(user_dict)
        self.loading_zone()
        self.main()

    def loading_zone(self):
        def redraw_window():
            self.screen.fill((27,31,35))
            join_btn.draw((240,240,240),join_the_game)
            players.draw("draw", f"{connections} {'player' if connections==1 else 'players'} {'is' if connections==1 else 'are'} connected.", (self.WIDTH / 2), (self.HEIGHT / 2) * 0.4)
            join_hover = join_btn.is_hovered()
            join_click = join_btn.is_clicking()

            if join_hover:
                if not join_click:
                    mouse.mode = 1
                else:
                    mouse.mode = 2
            else:
                mouse.mode = 0
            mouse.draw()
            pygame.display.update()
        
        def join_the_game():
            self.join_game = True
        # Receive number of players
        running = True
        mouse = Mouse("Graphics/MainMenu/Mouse/mouse1.png", "Graphics/MainMenu/Mouse/mouse2.png", "Graphics/MainMenu/Mouse/mouse3.png")
        self.width_ratio = self.WIDTH / 1920
        self.height_ratio = self.HEIGHT / 1080
        
        # Variables
        players = Text(self.gameMenu.text_height, "Graphics/Fonts/Orbitron-Regular.ttf", (240, 240, 240), None, None, None, int(self.gameMenu.base_text_size * 3))
        join_btn = Button((39, 174, 96), (27,31,35), (self.gameMenu.settings.WIDTH/2), (self.gameMenu.settings.HEIGHT/2)*1.4-self.gameMenu.button_padding, "Graphics/Fonts/Orbitron-Medium.ttf", (27,31,35), (39, 174, 96), self.gameMenu.base_button_width, self.gameMenu.base_button_height,'Start','Rectangle', None, int(self.gameMenu.big_text_size/1.3), self.gameMenu.curve)
        connections = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit()
                    
            try:
                connected_players = self.encryption.decrypt(self.unserialize(self.network.receive(self.DATA_SIZE)))
                connections = connected_players['connections']
                started = connected_players['started']
                if self.join_game and connections < 2:
                    self.join_game = False
                if started:
                    self.join_game = started
                game_dict = {"ready":self.join_game}
                start_the_game = self.serialize(self.encryption.encrypt(game_dict))
                self.network.send(start_the_game)
                if self.join_game or started:
                    self.join_game = True
                    running = False

            except:
                running = False
                logger.error("Something failed.")
                self.close()
                
            redraw_window()

if __name__ == "__main__":
    try:
        client = Client()
        client.run()
    except:
        logger.error("Couldn't run main menu or client.")
