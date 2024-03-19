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

	def create_particles(self,animation_type,pos,groups):
		animation_frames = self.frames[animation_type]
		animation_images = self.images[animation_type]
		self.particles = ParticleEffect(pos,animation_frames,animation_images,groups)

class ParticleEffect(pygame.sprite.Sprite):
	def __init__(self,pos,animation_frames,animation_images,groups):
		super().__init__(groups)
		self.settings = Config()
		self.sprite_type = 'magic'
		self.id = self.create_id()
		self.frame_index = 0
		self.animation_speed = 0.15
		self.frames = animation_frames
		self.images = animation_images
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = pos)

	def animate(self):
		self.frame_index += self.animation_speed
		if self.frame_index >= len(self.frames):
			self.kill()
		else:
			self.return_image()
			self.image = self.frames[int(self.frame_index)]

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

	def update(self):
		self.animate()
