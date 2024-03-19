from Scripts.logger import *
try:
    import pygame, random
    from Scripts.settings import *
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")

logger.debug("RealDL Magic Code.")

class MagicPlayer(Config):
	def __init__(self,animation_player):
		Config.__init__(self)
		self.animation_player = animation_player

	def heal(self,player,strength,cost,groups):
		if player.energy >= cost:
			player.health += strength
			#player.energy -= cost
			if player.health >= player.stats['health']:
				player.health = player.stats['health']
			self.animation_player.create_particles('aura',player.rect.center,groups)
			self.animation_player.create_particles('heal',player.rect.center,groups)

	def flame(self,player,cost,groups):
		if player.energy >= cost:
			#player.energy -= cost

			if player.status.split('_')[0] == 'right': direction = pygame.math.Vector2(1,0)
			elif player.status.split('_')[0] == 'left': direction = pygame.math.Vector2(-1,0)
			elif player.status.split('_')[0] == 'up': direction = pygame.math.Vector2(0,-1)
			else: direction = pygame.math.Vector2(0,1)

			for i in range(1,6):
				if direction.x: #horizontal
					offset_x = (direction.x * i) * self.TILESIZE
					x = player.rect.centerx + offset_x + random.randint(-self.TILESIZE // 3, self.TILESIZE // 3)
					y = player.rect.centery + random.randint(-self.TILESIZE // 3, self.TILESIZE // 3)
					self.animation_player.create_particles('flame',(x,y),groups)
				else: # vertical
					offset_y = (direction.y * i) * self.TILESIZE
					x = player.rect.centerx + random.randint(-self.TILESIZE // 3, self.TILESIZE // 3)
					y = player.rect.centery + offset_y + random.randint(-self.TILESIZE // 3, self.TILESIZE // 3)
					self.animation_player.create_particles('flame',(x,y),groups)