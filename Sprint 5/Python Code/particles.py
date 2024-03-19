from Scripts.logger import * 
try:  
	import pygame, string, random
	from Scripts.settings import Config
	from Scripts.support import import_folder
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")

logger.debug("RealDL Magic Code.")

class AnimationPlayer:
	def __init__(self):
		self.particles = None
		self.frames = {
			# magic
			'flame': import_folder('Graphics/Game/particles/flame/frames'),
			'aura': import_folder('Graphics/Game/particles/aura'),
			'heal': import_folder('Graphics/Game/particles/heal/frames'),
			}
			
		
		self.images = {
			# magic
			'flame': import_folder('Graphics/Game/particles/flame/frames',None),
			'aura': import_folder('Graphics/Game/particles/aura',None),
			'heal': import_folder('Graphics/Game/particles/heal/frames',None),
			}

	def create_particles(self,animation_type,pos,strength,groups,player_id):
		animation_frames = self.frames[animation_type]
		animation_images = self.images[animation_type]
		self.particles = ParticleEffect(pos,animation_frames,animation_images,animation_type,groups,strength,player_id)

class ParticleEffect(pygame.sprite.Sprite):
	def __init__(self,pos,animation_frames,animation_images,animation_type,groups,strength=None,player_id=None):
		super().__init__(groups)
		self.settings = Config()
		self.sprite_type = 'magic'
		self.strength = strength
		self.damaged_player = False
		self.animation_type = animation_type
		self.id = self.create_id()
		self.player_id = player_id
		self.frame_index = 0
		self.animation_speed = 0.15*(self.settings.frame_increase_rate/1.5)
		self.frames = animation_frames
		self.images = animation_images
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = pos)

	def animate(self, dt):
		self.frame_index += self.animation_speed  * dt
		if self.frame_index >= len(self.frames):
			self.kill()
		else:
			self.image = self.frames[int(self.frame_index)]

	def return_type(self):
		return self.animation_type
	
	def return_strength(self):
		return self.strength

	def return_image(self):
		self.full_path = self.images[int(self.frame_index)]
		if "../" in self.full_path:
			self.full_path = self.full_path.replace("../","")
		return self.full_path
	
	def create_id(self):
		try:
			characters = string.ascii_letters + string.digits
			return ''.join(random.choice(characters) for _ in range(self.settings.ID_STRING_LENGTH))
		except:
			logger.error("Something went wrong with creating a unique ID.")

	def update(self, dt):
		self.animate(dt)
