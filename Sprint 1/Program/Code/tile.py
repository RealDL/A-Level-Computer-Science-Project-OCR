import pygame
from settings import *
from logger import *

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
			self.id = id
		except FileExistsError as FileError:
			logger.error(f"Failed to create Tile Class: {FileError}")
