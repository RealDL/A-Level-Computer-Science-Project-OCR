from Scripts.logger import *
try:
	import pygame
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")
font = pygame.font.Font(None,30)

logger.debug("RealDL Debug Code.")

def debug(info,x=10,y=10):
	display_surface = pygame.display.get_surface()
	debug_surf = font.render(str(info),True,'White')
	debug_rect = debug_surf.get_rect(center = (x,y))
	pygame.draw.rect(display_surface,'Black',debug_rect)
	display_surface.blit(debug_surf,debug_rect)
