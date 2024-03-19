from Scripts.functions import *
from Scripts.logger import *
import pygame

logger.debug("RealDL UI Code.")

class UI:
    def __init__(self, custom_mouse, quit_function):
        # Setup Pygame Variables
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
        self.image_width = int(self.IMAGE_WIDTH*self.width_ratio)
        self.image_height = int(self.IMAGE_HEIGHT*self.height_ratio)
        self.image_padding = int(self.IMAGE_PADDING*self.width_ratio)
        self.button_padding = int(self.BUTTON_PADDING*self.height_ratio)
        self.text_height = int(self.TEXT_HEIGHT*self.height_ratio)
        self.base_text_size = int(self.BASE_TEXT_SIZE*self.height_ratio)
        self.big_text_size = int(self.BIG_TEXT_SIZE*self.height_ratio)
        self.curve = int(self.CURVE*self.height_ratio)
        self.thickness = int(self.THICKNESS*self.height_ratio)
        self.base_button_width = int(self.BASE_BUTTON_WIDTH*self.width_ratio)
        self.base_button_height = int(self.BASE_BUTTON_HEIGHT*self.height_ratio)

        # UI Board
        self.border = Button((27,31,35), (27,31,35), self.screen_width/2, self.screen_height/2, "Fonts/Orbitron-Regular.ttf", (27,31,35), (27,31,35), self.screen_width*0.7, self.screen_height*0.7,'','Rectangle', None, self.big_text_size, int(self.curve*1.5))
        self.join_boarder = Button((27,31,35), (27,31,35), (self.screen_width/2), (self.screen_height/2), "Fonts/Orbitron-Regular.ttf", (240,240,240), (136,173,227), self.base_button_width*3, self.base_button_height*6,'','Rectangle', None, self.big_text_size, self.curve)
        self.info = Text(self.text_height, "Fonts/Orbitron-Regular.ttf",(240,240,240), None, None, None, int(self.base_text_size*1.7))
        self.info2 = Text(self.text_height, "Fonts/Orbitron-Regular.ttf",(240,240,240), None, None, None, int(self.base_text_size*1.7))
        self.quit = Button((174, 39, 96), (27,31,35), self.screen_width/2, self.screen_height*0.78, "Fonts/Orbitron-Medium.ttf", (27,31,35), (174, 39, 96), self.base_button_width, self.base_button_height,'Quit','Rectangle', None, int(self.big_text_size/1.3), self.curve)
        self.bullet_assault = Text(self.text_height, "Fonts/Orbitron-Bold.ttf",(240,240,240), None, None, None, int(self.base_text_size*3.5))
        self.continue_btn = Button((39, 174, 96), (27,31,35), (self.screen_width/2), (self.screen_height/2)*1.445-self.button_padding, "Fonts/Orbitron-Medium.ttf", (27,31,35), (39, 174, 96), self.base_button_width, self.base_button_height,'Continue','Rectangle', None, int(self.big_text_size/1.3), self.curve)

    def stop_drawing(self):
        self.draw_ui = False

    def draw_menu(self):
        if self.draw_ui:
            self.border.draw((27,31,35),None, None, False)
            self.join_boarder.draw((240,240,240))
            self.info.draw("draw","Game Paused: You have entered the main menu.",(self.screen_width/2), (self.screen_height/2)*0.665)
            self.info2.draw("draw","Movement is currently disabled.",(self.screen_width/2), (self.screen_height/2)*0.72)
            self.quit.draw((240,240,240),self.quit_function)
            self.continue_btn.draw((240,240,240),self.stop_drawing)
            self.bullet_assault.draw("draw","Bullet Assault", (self.screen_width/2), (self.screen_height/2)*0.43)

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