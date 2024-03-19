from Scripts.logger import *
try:
    import pygame, math
    from Scripts.support import import_folder
    from Scripts.settings import Config
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")

logger.debug("RealDL Player Code.")

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, image, groups, obstacle_sprites, username, id, health, create_attack=None, destroy_attack=None, create_bullet=None, create_magic=None, movement="WASD", offense="Space", magic="L-Shift",status_alive="alive"):
        # Setting up player
        try:
            super().__init__(groups)
            self.settings = Config()
            self.screen = pygame.display.get_surface()
            try: 
                self.image = pygame.image.load(image).convert_alpha()
                self.image_name = image
            except: 
                self.image = pygame.image.load(f"../{image}").convert_alpha()
                self.image_name = f"../{image}"
            self.rect = self.image.get_rect(topleft = pos)
            self.hitbox = self.rect.inflate(0,-26)
            self.old_hitbox = self.hitbox.copy()
            self.pos = pygame.math.Vector2(self.hitbox.topleft)
            self.movement = movement
            self.offense = offense
            self.magic_key = magic
            self.key_binds = {
                'move_up': pygame.K_w if self.movement == "WASD" else pygame.K_UP,
                'move_down': pygame.K_s if self.movement == "WASD" else pygame.K_DOWN,
                'move_left': pygame.K_a if self.movement == "WASD" else pygame.K_LEFT,
                'move_right': pygame.K_d if self.movement == "WASD" else pygame.K_RIGHT,
                'attack': pygame.K_SPACE if self.offense == "Space" else pygame.K_LCTRL if self.offense == "L-Ctrl" else pygame.K_RCTRL,
                'magic': pygame.K_LSHIFT if self.magic_key == "L-Shift" else pygame.K_RSHIFT if self.magic_key == "R-Shift" else pygame.K_RETURN
                }

            # graphics setup
            self.import_player_assets()
            self.status = 'down'
            self.frame_index = 0
            self.animation_speed = 0.15*(self.settings.frame_increase_rate)*0.6

            # Movement
            self.direction = pygame.math.Vector2()
            self.attacking = False
            self.magic_attacking = False
            self.holding_attack_btn = False
            self.holding_magic_btn = False
            self.attack_cooldown = 400
            self.attack_time = None
            self.paused = False

            # weapon
            self.create_attack = create_attack
            self.destroy_attack = destroy_attack
            self.create_bullet = create_bullet
            self.weapon_index = 0
            self.weapon = list(self.settings.weapon_data.keys())[self.weapon_index]
            self.weapon_type = self.settings.weapon_data[self.weapon]['type']
            self.can_switch_weapon = True
            self.weapon_switch_time = None
            self.switch_duration_cooldown = 200

            # magic 
            self.magic_index = 0
            self.create_magic = create_magic
            self.magic = list(self.settings.magic_data.keys())[self.magic_index]
            self.can_switch_magic = True
            self.magic_switch_time = None

            # magic and weapons
            self.attacking_reset = False
            self.finish_attacking = 0

            # stats
            self.stats = {'health': 100,'energy':60,'attack': 10,'magic': 4,'speed': 6}
            #self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic' : 10, 'speed': 10}
            self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic' : 100, 'speed': 100}
            self.health = health
            self.energy = self.stats['energy'] * 0.8
            self.attack_strength = self.stats['attack']
            self.exp = 500
            self.speed = self.stats['speed']*(self.settings.frame_increase_rate/1.55)
            self.status_alive = status_alive

            # damage timer
            self.vulnerable = True
            self.hurt_time = None
            self.invulnerability_duration = 500
            self.alpha = 255
            self.image_alpha = 255
            
            #Other stats
            self.kill_count = 0
            self.username = username
            self.id = id
            self.basefont = "Graphics/Fonts/Orbitron-Medium.ttf"
            self.largefont = "Graphics/Fonts/Orbitron-Bold.ttf"
            self.textSize = 20
            try:
                self.font = pygame.font.Font(self.basefont, self.textSize)
                self.large_font = pygame.font.Font(self.largefont, self.textSize)
            except:
                self.font = pygame.font.Font(f"../{self.basefont}", self.textSize)
                self.large_font = pygame.font.Font(f"../{self.largefont}", self.textSize)

            self.sprite_type = "player"

            self.obstacle_sprites = obstacle_sprites
        except:
            logger.error("Failed to create Player Class")

    def import_player_assets(self):
        character_path = 'Graphics/Game/player/'
        self.animations = {'up': [],'down': [],'left': [],'right': [],
			'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
			'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]}
        
        self.animation_images = {'up': [],'down': [],'left': [],'right': [],
			'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
			'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation],self.animation_images[animation] = import_folder(full_path,True)

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.paused:
            if not self.attacking and not self.magic_attacking:
                if keys[self.key_binds['move_up']]:
                    self.direction.y = -1
                    self.status = 'up'
                elif keys[self.key_binds['move_down']]:
                    self.direction.y = 1
                    self.status = 'down'
                else:
                    self.direction.y = 0

                if keys[self.key_binds['move_right']]:
                    self.direction.x = 1
                    self.status = 'right'
                elif keys[self.key_binds['move_left']]:
                    self.direction.x = -1
                    self.status = 'left'
                else:
                    self.direction.x = 0

                if self.status_alive == "alive":
                    # attack input 
                    if keys[self.key_binds['attack']] and not self.magic_attacking and not self.attacking_reset:
                        self.attacking = True
                        self.holding_attack_btn = True
                        self.attack_time = pygame.time.get_ticks()
                        if self.create_attack != None:
                            self.create_attack(self.weapon_type)
                            if self.weapon_type == "gun":
                                if self.create_bullet:
                                    self.create_bullet()

                    # magic input 
                    if keys[self.key_binds['magic']] and not self.attacking and not self.attacking_reset:
                        self.magic_attacking = True
                        self.holding_magic_btn = True
                        self.attack_time = pygame.time.get_ticks()
                        style = list(self.settings.magic_data.keys())[self.magic_index]
                        strength = list(self.settings.magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
                        cost = list(self.settings.magic_data.values())[self.magic_index]['cost']
                        if self.create_magic:
                            self.create_magic(style,strength,cost)

                if keys[pygame.K_q] and self.can_switch_weapon:
                    self.can_switch_weapon = False
                    self.weapon_switch_time = pygame.time.get_ticks()
                    
                    if self.weapon_index < len(list(self.settings.weapon_data.keys())) - 1:
                        self.weapon_index += 1
                    else:
                        self.weapon_index = 0
                        
                    self.weapon = list(self.settings.weapon_data.keys())[self.weapon_index]
                    self.weapon_type = self.settings.weapon_data[self.weapon]['type']

                if keys[pygame.K_e] and self.can_switch_magic:
                    self.can_switch_magic = False
                    self.magic_switch_time = pygame.time.get_ticks()
                    
                    if self.magic_index < len(list(self.settings.magic_data.keys())) - 1:
                        self.magic_index += 1
                    else:
                        self.magic_index = 0

                    self.magic = list(self.settings.magic_data.keys())[self.magic_index]

            else:
                if not keys[self.key_binds['attack']]:
                    self.holding_attack_btn = False
                if not keys[self.key_binds['magic']]:
                    self.holding_magic_btn = False

    def get_status(self):
		# idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'

        if self.attacking or self.magic_attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle','_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack','')      

    def move(self,speed, dt):
        if not self.paused:
            if self.hitbox.x != self.old_hitbox.x or self.hitbox.y != self.old_hitbox.y:
                if not 'idle' in self.status:
                    self.old_hitbox = self.hitbox.copy()
            
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()

            self.pos.x += self.direction.x * speed * dt
            self.hitbox.x = self.pos.x
            self.collision('horizontal')

            self.pos.y += self.direction.y * speed * dt
            self.hitbox.y = self.pos.y 
            self.collision('vertical')
            self.rect.center = self.hitbox.center

    def collision(self,direction):
        collision_sprites = pygame.sprite.spritecollide(self,self.obstacle_sprites,False)
        if collision_sprites:
            if direction == 'horizontal':
                for sprite in collision_sprites:
                    
                    # Collision on the right
                    if self.hitbox.right >= sprite.hitbox.left and self.old_hitbox.right <= sprite.old_hitbox.left:
                        self.hitbox.right = sprite.hitbox.left
                        self.pos.x = self.hitbox.x

                    # Collision on the left
                    if self.hitbox.left <= sprite.hitbox.right and self.old_hitbox.left >= sprite.old_hitbox.right:
                        self.hitbox.left = sprite.hitbox.right
                        self.pos.x = self.hitbox.x
             
            if direction == 'vertical':
                for sprite in collision_sprites:
                    # Collision on the bottom
                    if self.hitbox.bottom >= sprite.hitbox.top and self.old_hitbox.bottom <= sprite.old_hitbox.top:
                        self.hitbox.bottom = sprite.hitbox.top
                        self.pos.y = self.hitbox.y

                    # Collision on the top
                    if self.hitbox.top <= sprite.hitbox.bottom and self.old_hitbox.top >= sprite.old_hitbox.bottom:
                        self.hitbox.top = sprite.hitbox.bottom
                        self.pos.y = self.hitbox.y

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + self.settings.weapon_data[self.weapon]['cooldown']:
                if not self.holding_attack_btn:
                    self.attacking = False
                    self.attacking_reset = True
                    self.finish_attacking = pygame.time.get_ticks()
                    if self.destroy_attack != None:
                        self.destroy_attack()
            if current_time - self.attack_time >= self.settings.weapon_data[self.weapon]['cooldown']:
                if self.holding_attack_btn and self.weapon_type == "gun":
                    if self.create_bullet:
                        self.create_bullet()
                        self.attack_time = current_time

        if self.magic_attacking:
            if current_time - self.attack_time >= self.settings.magic_data[self.magic]['cooldown']:
                if not self.holding_magic_btn:
                    self.magic_attacking = False
                    self.attacking_reset = True
                    self.finish_attacking = pygame.time.get_ticks()
        
        if self.attacking_reset:
            if current_time - self.finish_attacking >= self.settings.attack_or_magic_cooldown:
                self.attacking_reset = False

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def get_image_name(self):
        if "../" in self.image_name:
            self.image_name = self.image_name.replace("../","")
        return self.image_name

    def animate(self, dt):
        if not self.paused:
            animation = self.animations[self.status]
            image = self.animation_images[self.status]

            # loop over the frame index 
            self.frame_index += self.animation_speed * dt
            if self.frame_index >= len(animation):
                self.frame_index = 0

            # set the image
            self.image = animation[int(self.frame_index)]
            self.image_name = image[int(self.frame_index)]
            self.rect = self.image.get_rect(center = self.hitbox.center)
            
            #flicker
            self.flicker()

    def set_opacity(self):
        self.image.set_alpha(self.alpha)

    def return_alpha(self):
        return self.image_alpha

    def flicker(self):
        # flicker 
        if not self.vulnerable:
            self.image_alpha = self.wave_value()
            self.image.set_alpha(self.image_alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        base_damage = self.stats['attack']
        weapon_damage = self.settings.weapon_data[self.weapon]['damage']
        return base_damage + weapon_damage

    def get_full_magic_damage(self):
        base_damage = self.stats['magic']
        spell_damage = self.settings.magic_data[self.magic]['strength']
        return base_damage + spell_damage

    def get_value_by_index(self,index):
        return list(self.stats.values())[index]

    def get_cost_by_index(self,index):
        return list(self.upgrade_cost.values())[index]

    def energy_recovery(self):
        if self.energy < self.stats['energy']:
            self.energy += 0.002 * self.stats['magic']
        else:
            self.energy = self.stats['energy']

    def damage_player(self,damage):
        if self.vulnerable:
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()
            if self.health - damage <= 0:
                self.health = 0
                self.status_alive = "dead"
            else:
                self.health -= damage
            
    def return_alive_status(self):
        return self.status_alive

    def wave_value(self):
        value = math.sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0

    def draw(self, offset_pos, color=(190, 40, 50)):
        # Draw the player.
        alpha = 255
        if self.status_alive == "dead":
            color = (128, 128, 128)
            alpha = 135
        draw_image = self.image.copy()
        draw_image.set_alpha(alpha)
        text_surface = self.large_font.render(self.username, True, color)
        text_rect = text_surface.get_rect()
        username_pos = (offset_pos[0] + self.rect.width // 2 - text_surface.get_width() // 2, offset_pos[1] - 35)
        
        # Define the dimensions and position of the black box
        box_width = text_rect.width + 6  # Adjust the width as needed
        box_height = text_rect.height + 6  # Adjust the height as needed
        box_pos = (username_pos[0]-3, username_pos[1]-3) # Adjust the position as needed
        
        # Draw the black box
        pygame.draw.rect(self.screen, (27,31,35), ((box_pos[0]-2,box_pos[1]-2), (box_width+4, box_height+4)),3,10)
        #pygame.draw.rect(self.screen, (27,31,35), (box_pos, (box_width, box_height)),0,10)
        self.screen.blit(draw_image, offset_pos)
        self.screen.blit(text_surface, username_pos)

    def update(self, dt):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate(dt)
        self.move(self.speed, dt)
        self.energy_recovery()
        