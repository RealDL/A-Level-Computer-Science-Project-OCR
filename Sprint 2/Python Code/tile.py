import pygame
from Scripts.settings import *
from Scripts.logger import *

logger.debug("RealDL Tile Code.")

class Tile(pygame.sprite.Sprite):
	def __init__(self,pos,groups,image,id):
		try:
			super().__init__(groups)
			try:
				self.image = pygame.image.load(image).convert_alpha()
			except:
				self.image = pygame.image.load(f"../{image}").convert_alpha()
			self.rect = self.image.get_rect(topleft = pos)
			self.hitbox = self.rect.inflate(0,-10)
			self.id = id
			self.sprite_type = "tile"
		except FileExistsError as FileError:
			logger.error(f"Failed to create Tile Class: {FileError}")
