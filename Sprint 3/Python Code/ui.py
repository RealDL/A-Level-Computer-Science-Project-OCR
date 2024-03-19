from Scripts.logger import *
try:
    from Scripts.functions import *
    from Scripts.settings import Config
    import pygame
except:
    logger.critical("You do not have all the modules installed. Please install Pygame.")

logger.debug("RealDL UI Code.")

class UI(Config):
    def __init__(self, custom_mouse, quit_function, player_count, kill_count):
        # Setup Pygame Variables
        Config.__init__(self)
        self.screen = pygame.display.get_surface()
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        self.DEFAULT_WIDTH = 1920
        self.DEFAULT_HEIGHT = 1080
        self.width_ratio = self.screen_width / self.DEFAULT_WIDTH
        self.height_ratio = self.screen_height / self.DEFAULT_HEIGHT
        self.custom_mouse = custom_mouse
        self.draw_ui = False
        self.quit_function = quit_function

        # Constants setup
        self.BIG_TEXT_SIZE = 50
        self.BASE_TEXT_SIZE = 15
        self.TEXT_HEIGHT = 20
        self.IMAGE_WIDTH = 64
        self.IMAGE_HEIGHT = 64
        self.IMAGE_PADDING = 20
        self.BUTTON_PADDING = 85
        self.CURVE = 10
        self.THICKNESS = 2
        self.BASE_BUTTON_WIDTH = 250
        self.BASE_BUTTON_HEIGHT = 70

        # Variable setup
        self.image_width = int(self.IMAGE_WIDTH * self.width_ratio)
        self.image_height = int(self.IMAGE_HEIGHT * self.height_ratio)
        self.image_padding = int(self.IMAGE_PADDING * self.width_ratio)
        self.button_padding = int(self.BUTTON_PADDING * self.height_ratio)
        self.text_height = int(self.TEXT_HEIGHT * self.height_ratio)
        self.base_text_size = int(self.BASE_TEXT_SIZE * self.height_ratio)
        self.big_text_size = int(self.BIG_TEXT_SIZE * self.height_ratio)
        self.curve = int(self.CURVE * self.height_ratio)
        self.thickness = int(self.THICKNESS * self.height_ratio)
        self.base_button_width = int(self.BASE_BUTTON_WIDTH * self.width_ratio)
        self.base_button_height = int(self.BASE_BUTTON_HEIGHT * self.height_ratio)

        # UI Board
        self.border = Button((27, 31, 35), (27, 31, 35), self.screen_width / 2, self.screen_height / 2, "Graphics/Fonts/Orbitron-Regular.ttf", (27, 31, 35), (27, 31, 35), self.screen_width * 0.7, self.screen_height * 0.7, '', 'Rectangle', None, self.big_text_size, int(self.curve * 1.5))
        self.join_boarder = Button((27, 31, 35), (27, 31, 35), (self.screen_width / 2), (self.screen_height / 2), "Graphics/Fonts/Orbitron-Regular.ttf", (240, 240, 240), (136, 173, 227), self.base_button_width * 3, self.base_button_height * 6, '', 'Rectangle', None, self.big_text_size, self.curve)
        self.info = Text(self.text_height, "Graphics/Fonts/Orbitron-Regular.ttf", (240, 240, 240), None, None, None, int(self.base_text_size * 1.7))
        self.info2 = Text(self.text_height, "Graphics/Fonts/Orbitron-Regular.ttf", (240, 240, 240), None, None, None, int(self.base_text_size * 1.7))
        self.quit = Button((174, 39, 96), (27, 31, 35), self.screen_width / 2, self.screen_height * 0.78, "Graphics/Fonts/Orbitron-Medium.ttf", (27, 31, 35), (174, 39, 96), self.base_button_width, self.base_button_height, 'Quit', 'Rectangle', None, int(self.big_text_size / 1.3), self.curve)
        self.bullet_assault = Text(self.text_height, "Graphics/Fonts/Orbitron-Bold.ttf", (240, 240, 240), None, None, None, int(self.base_text_size * 3.5))
        self.continue_btn = Button((39, 174, 96), (27, 31, 35), (self.screen_width / 2), (self.screen_height / 2) * 1.445 - self.button_padding, "Graphics/Fonts/Orbitron-Medium.ttf", (27, 31, 35), (39, 174, 96), self.base_button_width, self.base_button_height, 'Continue', 'Rectangle', None, int(self.big_text_size / 1.3), self.curve)

        # In-game UI. kill count, 
        # general
        try:
            self.font = pygame.font.Font(self.UI_FONT, self.UI_FONT_SIZE)
        except:
            self.font = pygame.font.Font(f"../{self.UI_FONT}", self.UI_FONT_SIZE)
        self.player_count = player_count
        self.kill_count = kill_count

        # Kill count and player count
        self.boarder_stats = Button(self.UI_BG_COLOR, self.UI_BG_COLOR, self.WIDTH-(self.HEALTH_BAR_WIDTH)/2-10-2, 10+(self.BAR_HEIGHT*1.25)+2, "Graphics/Fonts/Orbitron-Medium.ttf", self.TEXT_COLOR, self.TEXT_COLOR, (self.HEALTH_BAR_WIDTH), self.BAR_HEIGHT*2.5, "", 'Rectangle', None, self.UI_FONT_SIZE, 0)
        self.kill_count = Button(self.UI_BG_COLOR, self.UI_BG_COLOR, self.WIDTH-(self.HEALTH_BAR_WIDTH)/2-10-2, 13.5+(self.BAR_HEIGHT/2)+2, "Graphics/Fonts/Orbitron-Medium.ttf", self.TEXT_COLOR, self.TEXT_COLOR, (self.HEALTH_BAR_WIDTH), self.BAR_HEIGHT, f'Kill count: {self.kill_count}', 'Rectangle', None, self.UI_FONT_SIZE, 0)
        self.players_alive = Button(self.UI_BG_COLOR, self.UI_BG_COLOR, self.WIDTH-(self.HEALTH_BAR_WIDTH)/2-10-2, self.BAR_HEIGHT+16.5+(self.BAR_HEIGHT/2)+2, "Graphics/Fonts/Orbitron-Medium.ttf", self.TEXT_COLOR, self.TEXT_COLOR, (self.HEALTH_BAR_WIDTH), self.BAR_HEIGHT, f"Players alive: {self.player_count}", 'Rectangle', None, self.UI_FONT_SIZE, 0)

        # bar setup
        self.health_bar_rect = pygame.Rect(10, 10, self.HEALTH_BAR_WIDTH, self.BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10, 34, self.ENERGY_BAR_WIDTH, self.BAR_HEIGHT)

        # convert weapon dictionary
        self.weapon_graphics = []
        for weapon in self.weapon_data.values():
            weapon_path = weapon['graphic']
            try:
                weapon = pygame.image.load(weapon_path).convert_alpha()
            except:
                weapon = pygame.image.load(f"../{weapon_path}").convert_alpha()
            self.weapon_graphics.append(weapon)

        # convert magic dictionary
        self.magic_graphics = []
        for magic in self.magic_data.values():
            magic_path = magic['graphic']
            try:
                magic = pygame.image.load(magic_path).convert_alpha()
            except:
                magic = pygame.image.load(f"../{magic_path}").convert_alpha()
            self.magic_graphics.append(magic)

    def stop_drawing(self):
        self.draw_ui = False

    def draw_menu(self):
        if self.draw_ui:
            self.border.draw((27, 31, 35), None, None, False)
            self.join_boarder.draw((240, 240, 240))
            self.info.draw("draw", "Game Paused: You have entered the main menu.", (self.screen_width / 2), (self.screen_height / 2) * 0.665)
            self.info2.draw("draw", "Movement is currently disabled.", (self.screen_width / 2), (self.screen_height / 2) * 0.72)
            self.quit.draw((240, 240, 240), self.quit_function)
            self.continue_btn.draw((240, 240, 240), self.stop_drawing)
            self.bullet_assault.draw("draw", "Bullet Assault", (self.screen_width / 2), (self.screen_height / 2) * 0.43)

            start_back_hover = self.quit.is_hovered()
            join_hover = self.continue_btn.is_hovered()

            start_back_click = self.quit.is_clicking()
            join_click = self.continue_btn.is_clicking()

            if start_back_hover or join_hover:
                if not start_back_click and not join_click:
                    self.custom_mouse.mode = 1
                else:
                    self.custom_mouse.mode = 2
            else:
                self.custom_mouse.mode = 0

            # Draw the mouse
            self.custom_mouse.draw()

    def show_info(self):
        self.boarder_stats.draw(self.UI_BORDER_COLOR,None,None,False)
        self.kill_count.draw(None,None,None,False)
        self.players_alive.draw(None,None,None,False)

    def show_bar(self, current, max_amount, bg_rect, color):
        # draw bg
        pygame.draw.rect(self.screen, self.UI_BG_COLOR, bg_rect)

        # converting stat to pixel
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # drawing the bar
        pygame.draw.rect(self.screen, color, current_rect)
        pygame.draw.rect(self.screen, self.UI_BORDER_COLOR, bg_rect, 3)

    def show_exp(self, exp):
        text_surf = self.font.render(str(int(exp)), False, self.TEXT_COLOR)
        x = self.screen.get_size()[0] - 20
        y = self.screen.get_size()[1] - 20
        text_rect = text_surf.get_rect(bottomright=(x, y))

        pygame.draw.rect(self.screen, self.UI_BG_COLOR, text_rect.inflate(20, 20))
        self.screen.blit(text_surf, text_rect)
        pygame.draw.rect(self.screen, self.UI_BORDER_COLOR, text_rect.inflate(20, 20), 3)

    def selection_box(self, left, top, has_switched):
        bg_rect = pygame.Rect(left, top, self.ITEM_BOX_SIZE, self.ITEM_BOX_SIZE)
        pygame.draw.rect(self.screen, self.UI_BG_COLOR, bg_rect)
        if has_switched:
            pygame.draw.rect(self.screen, self.UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.screen, self.UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def weapon_overlay(self, weapon_index, has_switched):
        bg_rect = self.selection_box(10, self.HEIGHT-self.ITEM_BOX_SIZE-10, has_switched)
        weapon_surf = self.weapon_graphics[weapon_index]
        weapon_rect = weapon_surf.get_rect(center=bg_rect.center)

        self.screen.blit(weapon_surf, weapon_rect)

    def magic_overlay(self, magic_index, has_switched):
        bg_rect = self.selection_box(10+self.ITEM_BOX_SIZE+10, self.HEIGHT-self.ITEM_BOX_SIZE-10, has_switched)
        magic_surf = self.magic_graphics[magic_index]
        magic_rect = magic_surf.get_rect(center=bg_rect.center)

        self.screen.blit(magic_surf, magic_rect)

    def display(self, player):
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, self.HEALTH_COLOR)
        self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, self.ENERGY_COLOR)

        self.show_exp(player.exp)
        self.show_info()

        self.weapon_overlay(player.weapon_index, not player.can_switch_weapon)
        self.magic_overlay(player.magic_index, not player.can_switch_magic)
