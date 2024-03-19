from Scripts.logger import *
try:
	import pygame
	from Scripts.settings import *
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")

logger.debug("RealDL Tile Code.")

class Tile(pygame.sprite.Sprite):
	def __init__(self,pos,groups,sprite_type,surface,id):
		try:
			super().__init__(groups)
			self.settings = Config()
			self.sprite_type = sprite_type
			self.id = id
			self.image = surface
			if sprite_type == 'object': 
				self.rect = self.image.get_rect(topleft = (pos[0],pos[1] - self.settings.TILESIZE))
			else: 
				self.rect = self.image.get_rect(topleft = pos)
			self.hitbox = self.rect.inflate(0,-10)
			
		except:
			logger.error(f"Failed to create Tile Class.")
