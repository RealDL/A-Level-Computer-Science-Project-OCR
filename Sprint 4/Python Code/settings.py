from Scripts.logger import *
try:    
    from socket import gethostname, gethostbyname
    import pickle, pygame
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")
pygame.init()

logger.info("Github: https://github.com/TheRealDL1/Simple-Client-Server")
logger.debug("RealDL Settings Code.")

class Config():
    def __init__(self):
        # Screen Width and Height
        info = pygame.display.Info()
        max_width = info.current_w
        max_height = info.current_h
        self.HEIGHT = 720 #max_height # 720
        self.WIDTH = 1280 #max_width # 1280
        
        # Other Server/ Client Settings
        self.SQUARE_SIZE = 64
        self.BITS = 256
        self.FPS = 60
        self.HOST_NAME = gethostname()
        self.SERVER = gethostbyname(self.HOST_NAME)
        self.PORT = 5555
        self.ID_STRING_LENGTH = 20
        self.BG_COLOR = (113, 221, 238)
        self.DATA_SIZE = 4096
        self.SMALL_DATA = 32
        self.ENCRYPTION_DATA_SIZE = 1024
        self.TILESIZE = 64
        self.TILE_ID = 'Tile'

        # weapons 
        self.weapon_data = {
            'sword': {'cooldown': 100, 'speed': 0, 'damage': 15,'graphic':'Graphics/Game/weapons/sword/full.png','type':'melee'},
            'lance': {'cooldown': 400, 'speed': 0, 'damage': 30,'graphic':'Graphics/Game/weapons/lance/full.png','type':'melee'},
            'axe': {'cooldown': 300, 'speed': 0, 'damage': 20, 'graphic':'Graphics/Game/weapons/axe/full.png','type':'melee'},
            'rapier':{'cooldown': 50, 'speed': 0, 'damage': 8, 'graphic':'Graphics/Game/weapons/rapier/full.png','type':'melee'},
            'sai':{'cooldown': 80, 'speed': 0, 'damage': 10, 'graphic':'Graphics/Game/weapons/sai/full.png','type':'melee'},
            'revolver':{'cooldown': 1000, 'speed': 20, 'damage': 25, 'graphic':'Graphics/Game/weapons/revolver/full.png','type':'gun'},
            'msg':{'cooldown': 175, 'speed': 10, 'damage': 5, 'graphic':'Graphics/Game/weapons/msg/full.png','type':'gun'},
            'pistol':{'cooldown': 600, 'speed': 15, 'damage': 18, 'graphic':'Graphics/Game/weapons/pistol/full.png','type':'gun'}}

        # Bullets

        self.bullet_type = {
            'msg': {
                'down': 'Graphics/Game/bullets/msg/down.png',
                'left': 'Graphics/Game/bullets/msg/left.png',
                'right': 'Graphics/Game/bullets/msg/right.png',
                'up': 'Graphics/Game/bullets/msg/up.png',
                },
            'pistol': {
                'down': 'Graphics/Game/bullets/pistol/down.png',
                'left': 'Graphics/Game/bullets/pistol/left.png',
                'right': 'Graphics/Game/bullets/pistol/right.png',
                'up': 'Graphics/Game/bullets/pistol/up.png',
                },
            'revolver': {
                'down': 'Graphics/Game/bullets/revolver/down.png',
                'left': 'Graphics/Game/bullets/revolver/left.png',
                'right': 'Graphics/Game/bullets/revolver/right.png',
                'up': 'Graphics/Game/bullets/revolver/up.png',
                }
        }

        # magic
        self.magic_data = {
            'flame': {'strength': 5,'cost': 20,'graphic':'Graphics/Game/particles/flame/fire.png','type':'magic','cooldown':1000},
            'heal' : {'strength': 20,'cost': 10,'graphic':'Graphics/Game/particles/heal/heal.png','type':'magic','cooldown':800}}
        
        # ui 
        self.BAR_HEIGHT = 20
        self.HEALTH_BAR_WIDTH = 200
        self.ENERGY_BAR_WIDTH = 140
        self.ITEM_BOX_SIZE = 90
        self.UI_FONT = 'Graphics/Fonts/Orbitron-Medium.ttf'
        self.UI_FONT_SIZE = 18

        # general colors
        self.WATER_COLOR = (113, 221, 238)
        self.UI_BG_COLOR = (34, 34, 34)
        self.UI_BORDER_COLOR = (17, 17, 17)
        self.TEXT_COLOR = (238, 238, 238)

        # ui colors
        self.HEALTH_COLOR = (255, 0, 0)
        self.ENERGY_COLOR = (23, 108, 235)
        self.UI_BORDER_COLOR_ACTIVE = (255, 215, 0)

        # upgrade menu
        self.TEXT_COLOR_SELECTED = (17, 17, 17)
        self.BAR_COLOR = (238, 238, 238)
        self.BAR_COLOR_SELECTED = (17, 17, 17)
        self.UPGRADE_BG_COLOR_SELECTED = (238, 238, 238)
        
    def serialize(self, data):
        try:
            return pickle.dumps(data)
        except pickle.PicklingError as Error:
            logger.error(f"Failed to pickle data: {Error}")
    
    def unserialize(self, data):
        try:
            return pickle.loads(data)
        except pickle.UnpicklingError as Error:
            logger.error(f"Failed to unpickle data: {Error}")

# This class is used for the client and the server.
# This means that if you are the server then you can keep this bit of code.
# But if you are not the server, but still on the same computer (assuming you have the same ipv4) then you will be fine.
# You will need to change this if you are running a Client instance from another computer.
# 
# ^
# |
# 
# Not needed as the server and client handle the IP.
