from Scripts.logger import *
try:
    import pygame
    from Scripts.settings import Config
    from Scripts.tile import Tile
    from Scripts.support import *
    from random import choice
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")

logger.info("RealDL Level Code.")

class Level(Config):
    def __init__(self):
        Config.__init__(self)

        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        self.player_sprites = pygame.sprite.Group()

        # sprite setup
        self.tile_id = 0
        self.create_map()

    def create_map(self):
        layouts = {
			'boundary': import_csv_layout('Map/map_FloorBlocks.csv'),
			'grass': import_csv_layout('Map/map_Grass.csv'),
			'object': import_csv_layout('Map/map_Objects.csv'),
		}

        graphics = {
			'grass': import_folder('Graphics/Game/grass'),
			'objects': import_folder('Graphics/Game/objects')
		}

        for style,layout in layouts.items():
            for row_index,row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * self.TILESIZE
                        y = row_index * self.TILESIZE
                        if style == 'boundary':
                            Tile((x,y),[self.obstacle_sprites],'invisible',pygame.Surface((self.TILESIZE,self.TILESIZE)),self.TILE_ID)
                        if style == 'grass':
                            tile_id = f"Tile{self.tile_id}"
                            if col == '8': 
                                grass_image = graphics['grass'][0]
                            elif col == '9':
                                grass_image = graphics['grass'][1]
                            else:
                               grass_image = graphics['grass'][2]
                            
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites,self.attackable_sprites],'grass',grass_image,tile_id)
                            self.tile_id += 1
                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf,self.TILE_ID)

    def run(self, player, dt):
        # update and draw the game
        self.visible_sprites.custom_draw(player)
        self.visible_sprites.update(dt)

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        # general setup
        super().__init__()
        self.settings = Config()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # Floor
        try: self.floor_surf = pygame.image.load('Graphics/Game/tilemap/bg.png').convert()
        except: self.floor_surf = pygame.image.load('../Graphics/Game/tilemap/bg.png').convert()

        self.floor_rect = self.floor_surf.get_rect(topleft=(0,0))  # in order to not see the white

    def custom_draw(self, player):
        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        self.display_surface.fill(self.settings.BG_COLOR)
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            if sprite.sprite_type == "player":
                if sprite.id == player.id:
                    sprite.draw(offset_pos, (50, 190, 40))  
                else:
                    if player.status_alive == "alive":
                        if not sprite.status_alive == "dead":
                            sprite.draw(offset_pos)
                    else:
                        sprite.draw(offset_pos)
            else:
                self.display_surface.blit(sprite.image, offset_pos)

# What we need to do is move everything else (including other players) relative towards the player.
# Pretty much all the sprites need to be updated here but we need to find a better way in order to draw
# the tiles to move and the player + the other players. the player should stay neutral in the middle.
# but we need to get all players too. Good luck future me. 🙏 Good bye 22:23 04/08/2023
