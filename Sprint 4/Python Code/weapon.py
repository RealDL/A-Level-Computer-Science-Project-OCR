from Scripts.logger import *
try:
    import pygame, string, random
    from Scripts.settings import *
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")

logger.debug("RealDL Weapon Code.")

class Melee(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        try:
            super().__init__(groups)
            self.sprite_type = "weapon"
            self.settings = Config()
            self.id = self.create_id()
            self.time = pygame.time.get_ticks()
            self.last_shot_time = 0  # Initialize the last shot time to 0
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
    def __init__(self, groups, x, y, id, image, sprite_type="weapon_copy"):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.id = id
        self.x = x
        self.y = y
        self.full_path = image
        try:
            self.image = pygame.image.load(self.full_path).convert_alpha()
        except:
            self.image = pygame.image.load(f"../{self.full_path}").convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Bullets(pygame.sprite.Sprite):
    def __init__(self, player, groups, obstacle_sprites):
        super().__init__(groups)
        self.settings = Config()
        self.obstacle_sprites = obstacle_sprites
        self.sprite_type = "bullet"
        self.id = self.create_id()
        self.player = player
        self.groups = groups
        self.direction = player.status.split('_')[0]
        gun = player.weapon
        self.speed = self.settings.weapon_data[gun]['speed']
        self.damage = player.attack_strength + self.settings.weapon_data[gun]['damage']
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

    def update(self):
        self.collision('horizontal')
        self.collision('vertical')
        if not self.collided:
            if self.direction == 'right':
                self.rect.x += self.speed
            elif self.direction == 'left':
                self.rect.x -= self.speed
            elif self.direction == 'down':
                self.rect.y += self.speed
            else:
                self.rect.y -= self.speed

        if self.collided:
            self.kill()

    def create_id(self):
        try:
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(self.settings.ID_STRING_LENGTH))
        except:
            logger.error("Something went wrong with creating a unique ID.")

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.rect):
                    self.collided = True

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.rect):
                    self.collided = True

        # You may want to set its initial position and direction here

