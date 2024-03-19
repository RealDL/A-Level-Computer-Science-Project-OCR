import pygame
from logger import *

logger.debug("RealDL Player Code.")

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, image, groups, obstacle_sprites, id):
        # Setting up player
        try:
            super().__init__(groups)
            try:
                self.image = pygame.image.load(image).convert_alpha()
            except:
                self.image = pygame.image.load(f"../{image}").convert_alpha()
            self.rect = self.image.get_rect(topleft = pos)
            self.direction = pygame.math.Vector2()
            self.speed = 5
            self.id = id

            self.obstacle_sprites = obstacle_sprites
        except FileExistsError as FileError:
            logger.error(f"Failed to create Player Class: {FileError}")

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        else:
            self.direction.x = 0

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

    def move(self,speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * speed
        self.collision('horizontal')
        self.rect.y += self.direction.y * speed
        self.collision('vertical')

    def collision(self,direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.x > 0: # moving right
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0: # moving left
                        self.rect.left = sprite.rect.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.y > 0: # moving down
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0: # moving up
                        self.rect.top = sprite.rect.bottom

    def update(self):
        self.input()
        self.move(self.speed)
        
