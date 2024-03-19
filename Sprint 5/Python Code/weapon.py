from Scripts.logger import *
try:
    import pygame, string, random
    from Scripts.settings import *
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")

logger.debug("RealDL Weapon Code.")

class Melee(pygame.sprite.Sprite):
    def __init__(self, player, groups, player_id):
        try:
            super().__init__(groups)
            self.sprite_type = "weapon"
            self.settings = Config()
            self.id = self.create_id()
            self.player_id = player_id
            self.time = pygame.time.get_ticks()
            self.last_shot_time = 0  # Initialize the last shot time to 0
            self.damage = player.attack_strength + self.settings.weapon_data[player.weapon]['damage']
            self.damaged_player = False
            direction = player.status.split('_')[0]
            
            # Load the image
            self.full_path = f'Graphics/Game/weapons/{player.weapon}/{direction}.png'
            try:
                self.image = pygame.image.load(self.full_path).convert_alpha()
            except:
                self.image = pygame.image.load(f"../{self.full_path}").convert_alpha()

            # Set the placement of the sprite
            if direction == 'right':
                self.rect = self.image.get_rect(midleft=player.rect.midright + pygame.math.Vector2(0, 16))
            elif direction == 'left':
                self.rect = self.image.get_rect(midright=player.rect.midleft + pygame.math.Vector2(0, 16))
            elif direction == 'down':
                self.rect = self.image.get_rect(midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
            else:
                self.rect = self.image.get_rect(midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))
        except:
            logger.error("Failed to create Weapon")

    def create_id(self):
        try:
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(self.settings.ID_STRING_LENGTH))
        except:
            logger.error("Something went wrong with creating a unique ID.")

class Weapon(pygame.sprite.Sprite):
    def __init__(self, groups, x, y, id, image, player_id, damage=None, sprite_type="weapon_copy"):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.id = id
        self.player_id = player_id
        self.x = x
        self.y = y
        self.full_path = image
        self.damage = damage
        self.damaged_player = False
        try:
            self.image = pygame.image.load(self.full_path).convert_alpha()
        except:
            self.image = pygame.image.load(f"../{self.full_path}").convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
    
    def return_image(self):
        if "../" in self.full_path:
            self.full_path = self.full_path.replace("../","")
        return self.full_path

class Bullets(pygame.sprite.Sprite):
    def __init__(self, player, groups, obstacle_sprites, player_id, player_group):
        super().__init__(groups)
        self.settings = Config()
        self.obstacle_sprites = obstacle_sprites
        self.sprite_type = "bullet"
        self.id = self.create_id()
        self.player_id = player_id
        self.player_group = player_group
        self.player = player
        self.direction = player.status.split('_')[0]
        gun = player.weapon
        self.speed = self.settings.weapon_data[gun]['speed']*self.settings.frame_increase_rate/1.5
        self.damage = player.attack_strength + self.settings.weapon_data[gun]['damage']
        self.damaged_player = False
        self.cooldown = self.settings.weapon_data[gun]['cooldown']
        self.collided = False

        self.full_path = self.settings.bullet_type[gun][self.direction]
        try:
            self.image = pygame.image.load(self.full_path).convert_alpha()
        except:
            self.image = pygame.image.load(f"../{self.full_path}").convert_alpha()
        
        # Set the placement of the sprite
        if self.direction == 'right':
            self.rect = self.image.get_rect(midleft=player.rect.midright + pygame.math.Vector2(20, 8))
        elif self.direction == 'left':
            self.rect = self.image.get_rect(midright=player.rect.midleft + pygame.math.Vector2(-20, 8))
        elif self.direction == 'down':
            self.rect = self.image.get_rect(midtop=player.rect.midbottom + pygame.math.Vector2(-18, 21))
        else:
            self.rect = self.image.get_rect(midbottom=player.rect.midtop + pygame.math.Vector2(-18, -21))

    def update(self, dt):
        self.collision('obstacle')
        self.collision('player')
        if not self.collided:
            if self.direction == 'right':
                self.rect.x += self.speed * dt
            elif self.direction == 'left':
                self.rect.x -= self.speed * dt
            elif self.direction == 'down':
                self.rect.y += self.speed * dt
            else:
                self.rect.y -= self.speed * dt

        if self.collided:
            self.kill()

    def create_id(self):
        try:
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(self.settings.ID_STRING_LENGTH))
        except:
            logger.error("Something went wrong with creating a unique ID.")

    def collision(self, collision_type):
        if collision_type == "obstacle":
            collision_sprites = pygame.sprite.spritecollide(self,self.obstacle_sprites,False)
            if collision_sprites:
                self.collided = True
        
        if collision_type == "player":
            collision_sprites = pygame.sprite.spritecollide(self,self.player_group,False)
            if collision_sprites:
                self.collided = True
                
        """if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.rect):
                    self.collided = True
            for sprite in self.player_group:
                if sprite.hitbox.colliderect(self.rect):
                    self.collided = True

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.rect):
                    self.collided = True
            for sprite in self.player_group:
                if sprite.hitbox.colliderect(self.rect):
                    self.collided = True"""

        # You may want to set its initial position and direction here

