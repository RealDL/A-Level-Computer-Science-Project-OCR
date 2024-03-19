import pygame
from Scripts.logger import *
from Scripts.support import import_folder

logger.debug("RealDL Player Code.")

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, image, groups, obstacle_sprites, username, id, movement="WASD", offense="Space"):
        # Setting up player
        try:
            super().__init__(groups)
            self.screen = pygame.display.get_surface()
            try: self.image = pygame.image.load(image).convert_alpha()
            except: self.image = pygame.image.load(f"../{image}").convert_alpha()
            self.image_name = f"../{image}"
            self.rect = self.image.get_rect(topleft = pos)
            self.hitbox = self.rect.inflate(0,-26)
            self.movement = movement
            self.offense = offense
            self.key_binds = {
                'move_up': pygame.K_w if self.movement == "WASD" else pygame.K_UP,
                'move_down': pygame.K_s if self.movement == "WASD" else pygame.K_DOWN,
                'move_left': pygame.K_a if self.movement == "WASD" else pygame.K_LEFT,
                'move_right': pygame.K_d if self.movement == "WASD" else pygame.K_RIGHT,
                'attack': pygame.K_SPACE if self.offense == "Space" else pygame.K_LCTRL if self.offense == "L-Ctrl" else pygame.K_RCTRL
                }

            # graphics setup
            self.import_player_assets()
            self.status = 'down'
            self.frame_index = 0
            self.animation_speed = 0.15

            # Movement
            self.direction = pygame.math.Vector2()
            self.speed = 5
            self.attacking = False
            self.attack_cooldown = 400
            self.attack_time = None
            self.paused = False
            
            #Other stats
            self.username = username
            self.id = id
            self.basefont = "Fonts/Orbitron-Medium.ttf"
            self.textSize = 20
            try:
                self.font = pygame.font.Font(self.basefont, self.textSize)
            except:
                self.font = pygame.font.Font(f"../{self.basefont}", self.textSize)
            self.sprite_type = "player"

            self.obstacle_sprites = obstacle_sprites
        except FileExistsError as FileError:
            logger.error(f"Failed to create Player Class: {FileError}")

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
            self.animations[animation],self.animation_images[animation] = import_folder(full_path)

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.paused:

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

            if keys[self.key_binds['attack']]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                logger.info('attack')

    def get_status(self):
		# idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'

        if self.attacking:
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

    def move(self,speed):
        if not self.paused:
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()

            self.hitbox.x += self.direction.x * speed
            self.collision('horizontal')
            self.hitbox.y += self.direction.y * speed
            self.collision('vertical')
            self.rect.center = self.hitbox.center

    def collision(self,direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False

    def get_image_name(self):
        image_to_return = self.image_name
        if "../" in image_to_return:
            image_to_return = self.image_name.replace("../","")
        return image_to_return

    def animate(self):
        if not self.paused:
            animation = self.animations[self.status]
            image = self.animation_images[self.status]

            # loop over the frame index 
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0

            # set the image
            self.image = animation[int(self.frame_index)]
            self.image_name = image[int(self.frame_index)]
            self.rect = self.image.get_rect(center = self.hitbox.center)

    def draw(self, offset_pos):
        # Draw the player.
        text_surface = self.font.render(self.username, True, (240,240,240))
        text_rect = text_surface.get_rect()
        username_pos = (offset_pos[0] + self.rect.width // 2 - text_surface.get_width() // 2, offset_pos[1] - 33)
        # Define the dimensions and position of the black box
        box_width = text_rect.width + 6  # Adjust the width as needed
        box_height = text_rect.height + 6  # Adjust the height as needed
        box_pos = (username_pos[0]-3, username_pos[1]-3)  # Adjust the position as needed
        
        # Draw the black box
        pygame.draw.rect(self.screen, (200,200,200), ((box_pos[0]-2,box_pos[1]-2), (box_width+4, box_height+4)),0,10)
        pygame.draw.rect(self.screen, (27,31,35), (box_pos, (box_width, box_height)),0,10)
        self.screen.blit(self.image, offset_pos)
        self.screen.blit(text_surface, username_pos)

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
        