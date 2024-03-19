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
        self.HEIGHT = max_height # 720
        self.WIDTH = max_width # 1280
        
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
            'sword': {'cooldown': 100, 'damage': 15,'graphic':'Graphics/Game/weapons/sword/full.png'},
            'lance': {'cooldown': 400, 'damage': 30,'graphic':'Graphics/Game/weapons/lance/full.png'},
            'axe': {'cooldown': 300, 'damage': 20, 'graphic':'Graphics/Game/weapons/axe/full.png'},
            'rapier':{'cooldown': 50, 'damage': 8, 'graphic':'Graphics/Game/weapons/rapier/full.png'},
            'sai':{'cooldown': 80, 'damage': 10, 'graphic':'Graphics/Game/weapons/sai/full.png'},
            'revolver':{'cooldown': 200, 'damage': 25, 'graphic':'Graphics/Game/weapons/revolver/full.png'},
            'msg':{'cooldown': 60, 'damage': 6, 'graphic':'Graphics/Game/weapons/msg/full.png'},
            'pistol':{'cooldown': 160, 'damage': 16, 'graphic':'Graphics/Game/weapons/pistol/full.png'}}

        # magic
        self.magic_data = {
            'flame': {'strength': 5,'cost': 20,'graphic':'Graphics/Game/particles/flame/fire.png'},
            'heal' : {'strength': 20,'cost': 10,'graphic':'Graphics/Game/particles/heal/heal.png'}}
        
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