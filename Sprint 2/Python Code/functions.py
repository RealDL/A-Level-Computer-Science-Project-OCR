import pygame
import webbrowser
from Scripts.logger import *
logger.info("Pygame Functions 0.0.1 (Python 3.11.0)\nI am not affliated with pygame. https://github.com/TheRealDL1/pygame_functions")

class Images(object):
    def __init__(self, image):
        self.image = image
        self.screen = pygame.display.get_surface()
        self.load_image = self.load_image_from_file()
        self.rect = self.load_image.get_rect()

    def load_image_from_file(self):
        try:
            return pygame.image.load(self.image).convert_alpha()
        except:
            return pygame.image.load(f"../{self.image}").convert_alpha()
            
    def display_icon(self):
        pygame.display.set_icon(self.load_image)

    def draw(self, x=0, y=0):
        self.screen.blit(self.load_image, (x,y))

    def resize(self, width, height):
        self.load_image = pygame.transform.scale(self.load_image, (width, height))

class Mouse(object):
    def __init__(self,mouse_image1, mouse_image2, mouse_image3):
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.get_surface()
        self.mode = 0
        self.mouse_mode1 = Images(mouse_image1)
        self.mouse_mode2 = Images(mouse_image2)
        self.mouse_mode3 = Images(mouse_image3)

    def draw(self):
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Draw a green square at the mouse cursor position
        if self.mode == 0:
            self.mouse_mode1.draw(mouse_x , mouse_y)
        elif self.mode == 1:
            self.mouse_mode2.draw(mouse_x , mouse_y)
        else:
            self.mouse_mode3.draw(mouse_x , mouse_y)

class WordButton(object):
    def __init__(self, x, y, text, color1, color2,  basefont, largefont, textSize=30,):
        """Sets the values for button"""
        self.color = color1
        self.color2 = color2
        self.x = x
        self.y = y
        self.text = text
        self.textSize = textSize
        self.largeSize = round(self.textSize * 1.25)
        self.basefont = basefont
        self.largefont = largefont
        try:
            self.base_font = pygame.font.Font(self.basefont, self.textSize)
            self.large_font = pygame.font.Font(self.largefont, self.largeSize)
        except:
            self.base_font = pygame.font.Font(f"../{self.basefont}", self.textSize)
            self.large_font = pygame.font.Font(f"../{self.largefont}", self.largeSize)
        self.hover = False
        self.click = False
        self.release = False

    def displayText(self, win, newText=None, action=None, link=None):
        if newText != None:
            self.text = newText
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        # Render text with both fonts
        text = self.large_font.render(self.text, 1, self.color2)
        text2 = self.base_font.render(self.text, 1, self.color)

        # Check if mouse is over the text
        if self.x + text.get_width()/2> mouse[0] > self.x - text.get_width()/2 and self.y + text.get_height()/2  > mouse[1] > self.y - text.get_height()/2:
            self.hover = True
            # Render text with larger font and lighter color
            text = self.large_font.render(self.text, 1, self.color2)

            # Center text vertically as well as horizontally
            win.blit(text, (self.x - text.get_width() / 2, self.y - text.get_height() / 2))

            # Check for mouse click and run action if specified
            if click[0] == 1:
                self.click = True
            
            if self.click == True and not click[0]:
                self.release = True
            
            if self.release:
                if action != None:
                    action()
                if link != None:
                    webbrowser.open(link)
                self.release = False
                self.click = False
        else:
            self.hover = False
            self.click = False
            self.release = False
            # Render text with base font and color
            text2 = self.base_font.render(self.text, 1, self.color)

            # Center text vertically as well as horizontally
            win.blit(text2, (self.x - text2.get_width() / 2, self.y - text2.get_height() / 2))

class Animation(object):
    def __init__(self, image, scale, scale_direction, scale_min, scale_max, scale_speed, screen_y, screen_x):
        self.scale = scale #1.0
        self.image = image
        self.scale_direction = scale_direction #-1.35  # Start by zooming out
        self.scale_min = scale_min #0.9
        self.scale_max = scale_max #1.2
        self.scale_speed = scale_speed #0.01  # The rate at which the scale changes
        self.screen_center_x = screen_x
        self.screen_center_y = screen_y #324#win.get_height() // 2
        self.monopoly_rect = self.image.get_rect(center=(self.screen_center_x, self.screen_center_y))

    def animation(self, win):
        self.scale += self.scale_direction * self.scale_speed
        if self.scale <= self.scale_min:
            if self.scale_direction < 0:
                self.scale_direction = self.scale_direction * -1
            else:
                self.scale_direction = self.scale_direction * 1# Start zooming in
        elif self.scale >= self.scale_max:
            if self.scale_direction > 0:
                self.scale_direction = self.scale_direction * -1
            else:
                self.scale_direction = self.scale_direction * 1  # Start zooming out

        # Scale the image and get its rect
        scaled_monopoly = pygame.transform.rotozoom(self.image, 0, self.scale)
        scaled_monopoly_rect = scaled_monopoly.get_rect(center=(self.screen_center_x, self.screen_center_y))

        # Blit the scaled image to the screen and update the display
        win.blit(scaled_monopoly, scaled_monopoly_rect)

class TextBox(object):
    def __init__(self, width, height, x, y, color1, color2, textfont, curve, thickness, maxTextWidth, text_size=50):
        self.text = ''
        self.textSize = text_size
        self.textfont = textfont
        try:
            self.base_font = pygame.font.Font(self.textfont, self.textSize)
        except: 
            self.base_font = pygame.font.Font(f"../{self.textfont}", self.textSize)
        self.active = False
        self.width = width
        self.height = height
        self.x = x - self.width / 2
        self.ogWidth = width
        self.y = y
        self.color_active = pygame.Color(color1)
        self.color_passive = pygame.Color(color2)
        self.color = self.color_passive
        self.last_update = 0 # time of last update
        self.show_cursor = False # whether to show cursor or not
        self.cursor = 0
        self.maxTextWidth = maxTextWidth
        self.curve = curve
        self.thickness = thickness
        self.screen = pygame.display.get_surface()
        self.hover = False
        self.click = False
    
    def draw(self):
        area = [self.x,self.y,self.width,self.height]
        pygame.draw.rect(self.screen, self.color, area, self.thickness, self.curve)
        
    def is_hovered(self):
        mouse = pygame.mouse.get_pos()
        return self.x + self.width > mouse[0] > self.x and self.y + self.height > mouse[1] > self.y
        
    def is_clicking(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        return self.x + self.width > mouse[0] > self.x and self.y + self.height > mouse[1] > self.y and click[0]

    def checkTextBox(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        if self.x + self.width > mouse[0] > self.x and self.y + self.height > mouse[1] > self.y:
            self.hover = True
            if click[0]: self.click = True
            if self.click and not click[0]: self.click = False
            if self.active: self.active = False
            else: self.active = True

        else:
            self.hover = False
            self.active = False
            self.click = False

        if self.active:
            self.color = self.color_active
        else:
            self.color = self.color_passive
            
    def update(self, color=(240,240,240),x_pos=None, y_pos=None):
        middleOfX = self.screen.get_width() // 2
        if x_pos: self.x = x_pos
        if y_pos: self.y = y_pos
        
        if self.text:
            surface_area = self.base_font.render(self.text, True, color)
            text_width = surface_area.get_width() + 20
            if self.ogWidth > self.width:
                self.width = self.ogWidth
                self.x = middleOfX - self.width // 2
            if text_width > self.width:
                self.width = text_width
                self.x = middleOfX - self.width // 2
            elif self.width > text_width:
                if self.ogWidth < self.width:
                    self.width = text_width
                    self.x = middleOfX - self.width // 2
            self.screen.blit(surface_area, (self.x + 5, self.y + (self.height // 2 - surface_area.get_height() // 2)))
        else:
            self.width = self.ogWidth
            self.x = middleOfX - self.width // 2
            surface_area = self.base_font.render(self.text, True, color)
            self.screen.blit(surface_area, (self.x + 5, self.y + (self.height // 2 - surface_area.get_height() // 2)))

        time_since_last_update = pygame.time.get_ticks() - self.last_update
        if self.active and time_since_last_update > 500:
            self.show_cursor = not self.show_cursor
            self.last_update = pygame.time.get_ticks()

        if self.show_cursor and self.active == True:
            cursor_width = 2
            cursor_pos = self.base_font.size(self.text[:self.cursor])[0] - 5
            text_to_show = self.text[:self.cursor] + '|' + self.text[self.cursor:]
            cursor_pos += self.base_font.size(' ')[0] * 0.8
            surface_area = self.base_font.render(text_to_show, True, color)
            cursor_area = pygame.Surface((cursor_width, surface_area.get_height()))
            cursor_area.fill(color)
            self.screen.blit(cursor_area, (self.x + cursor_pos, self.y + (self.height // 2 - cursor_area.get_height() // 2)), (0, 0, cursor_width, cursor_area.get_height()))
        #else:
            #surface_area = self.base_font.render(self.text, True, color)
            #self.screen.blit(surface_area, (self.x + 5, self.y + (self.height // 2 - surface_area.get_height() // 2)))

    def updateText(self, events, color=(0,0,0), function=None):
        surface_area = self.base_font.render(self.text, True, color)
        text_width = surface_area.get_width() + 20
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.checkTextBox()
            if event.type == pygame.KEYDOWN:
                if self.active == True:
                    if event.key == pygame.K_BACKSPACE:
                        if self.cursor > 0:
                            self.text = self.text[:self.cursor-1] + self.text[self.cursor:]
                            self.cursor -= 1
                    elif event.key == pygame.K_DELETE:
                        self.text = self.text[:self.cursor] + self.text[self.cursor+1:]
                    elif event.key == pygame.K_RETURN:
                        if function != None:
                            function()
                    elif event.key == pygame.K_LEFT:
                        if self.cursor > 0:
                            self.cursor -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.cursor < len(self.text):
                            self.cursor += 1
                    else:
                        if text_width < self.maxTextWidth and event.key is not pygame.K_TAB:
                            new_text = self.text[:self.cursor] + event.unicode + self.text[self.cursor:]
                            if len(new_text) > len(self.text):
                                self.text = new_text
                                self.cursor += 1

    def return_text(self):
        return self.text

class Text(object):
    def __init__(self, height, baseFont, color=(0,0,0), x=None, y=None, text=None, textSize=32):
        self.text = text
        self.x = x
        self.y = y
        self.baseFont = baseFont
        self.height = height
        self.textSize = textSize
        self.color = color
        self.screen = pygame.display.get_surface()
        try:
            self.base_font = pygame.font.Font(self.baseFont, self.textSize)
        except:
            self.base_font = pygame.font.Font(f"../{self.baseFont}", self.textSize)
        self.hover = False
        self.click = False
        self.release = False

        # Animation
        self.stop_start_animation = True
        self.animation_time = 150
        self.animation_speed = 13
        self.num_frames = 60
        self.time = 0
        self.time2 = 0

        # Opacity
        self.opacitya = 0
        self.opacityb = 255
        self.opacity_color1 = 0
        self.opacity_color2 = 0
        self.opacity_color = 0

    def draw(self, mode="draw",new_text=None, new_x=None, new_y=None, function= None, link=None):
        if new_text: self.text = new_text
        if new_x: self.x = new_x
        if new_y: self.y = new_y

        if mode == "normal":
            surface_area = self.base_font.render(self.text, 1, self.color)
            self.screen.blit(surface_area, (self.x - surface_area.get_width() / 2, self.y - surface_area.get_height() / 2))

        if mode == "draw":
            self.stop_start_animation = False
            self.time = pygame.time.get_ticks()
            step = (self.time - self.time2) / (self.animation_time / self.animation_speed)
            self.opacity_color1 = self.change_opacity(self.opacity_color2, self.opacityb, step)
            self.opacity_color = self.opacity_color1

        if mode == "undraw":
            self.time2 = pygame.time.get_ticks()
            step = (self.time2 - self.time) / (self.animation_time / self.animation_speed)
            self.opacity_color2 = self.change_opacity(self.opacity_color1, self.opacitya, step)
            self.opacity_color = self.opacity_color2
        
        if not self.stop_start_animation:
            surface_area = self.base_font.render(self.text, 1, self.color)
            surface_area.set_alpha(self.opacity_color)
            self.screen.blit(surface_area, (self.x - surface_area.get_width() / 2, self.y - surface_area.get_height() / 2))

        if self.is_hovered(): self.hover = True
        if self.is_clicking(): self.click = True
        if self.click and not self.is_clicking(): self.release = True

        if self.release:
            if function: function()
            if link: webbrowser.open(link)

            self.release = False
            self.click = False

        if not self.is_hovered: 
            self.hover = False
            self.click = False
            self.release = False
    
    def change_opacity(self, original_opacity, new_opacity, step_multiplier=0):
        new_opacity_return = None
        difference = new_opacity - original_opacity
        opacity_step = difference / self.num_frames
        if original_opacity > new_opacity:
            if int(original_opacity + opacity_step*step_multiplier) < new_opacity:
                new_opacity_return = new_opacity
            else:
                new_opacity_return = int(original_opacity + opacity_step*step_multiplier)
        else:
            if int(original_opacity + opacity_step*step_multiplier) > new_opacity:
              new_opacity_return = new_opacity
            else:
                new_opacity_return = int(original_opacity + opacity_step*step_multiplier)
                
        return new_opacity_return
    
    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        text_rect = self.base_font.render(self.text, 1, self.color).get_rect()
        text_rect.center = (self.x, self.y)
        return text_rect.collidepoint(mouse_pos)

    def is_clicking(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        text_rect = self.base_font.render(self.text, 1, self.color).get_rect()
        text_rect.center = (self.x, self.y)
        return text_rect.collidepoint(mouse_pos) and mouse_buttons[0] == 1

class Button(object):
    """A class for all buttons"""
    def __init__(self, color, color2, x, y, basefont, text_color=(0,0,0), text_color2=(0,0,0), width=None, height=None, text='',buttonType='Rectangle', radius=None, textSize=30, curve=10, image=""):
        """Sets the values for buttton"""
        self.screen = pygame.display.get_surface()
        try:
            self.x = x - width/2
            self.y = y - height/2
            self.width = width
            self.height = height
        except:
            self.x = x
            self.y = y

        if image != "":
            self.image = Images(image)
            if height and width:
                self.image.resize(width,height)
        self.text = text
        self.buttonType = buttonType
        self.radius = radius
        self.textSize = textSize
        self.curve = curve
        #Mouse clicking
        self.hover = False
        self.click = False
        self.release = False
        # Animation
        self.stop_start_animation = True
        self.animation_time = 150
        self.animation_speed = 13
        self.num_frames = 60
        self.time = 0
        self.time2 = 0
        # Colors
        self.color = color
        self.color2 = color2
        self.text_color = text_color
        self.text_color2 = text_color2
        self.text_trans_color = self.text_color
        self.button_trans_color = self.color
        self.text_trans_color2 = self.text_color
        self.button_trans_color2 = self.color
        # Opacity
        self.opacitya = 255
        self.opacityb = 180
        self.opacity1 = 255
        self.opacity2 = 180
        # Fonts
        self.basefont = basefont
        try:
            self.base_font = pygame.font.Font(self.basefont, self.textSize)
        except:
            self.base_font = pygame.font.Font(f"../{self.basefont}", self.textSize)
    
    def draw(self,outline=None,action=None, link=None, colorChange=True, newText=None, newX=None, newY=None, mode="normal"):
        """New X, Y and Text values"""
        if newText: self.text = newText
        if newX: self.x = newX
        if newY: self.y = newY

        """Draws the button. Variable for mouse detection"""
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if self.buttonType == "Rectangle":
            """If it is a rectangle it will draw it here"""
            if mode == "normal":
                if outline:
                    """draws an outline"""
                    pygame.draw.rect(self.screen, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0,self.curve)
                if self.x+self.width > mouse[0] > self.x and self.y+self.height > mouse[1] > self.y and colorChange:
                    self.hover = True
                    self.stop_start_animation = False
                    self.time2 = pygame.time.get_ticks()
                    step = (self.time2 - self.time) / (self.animation_time / self.animation_speed)
                    """Draws a lighter version of the image"""
                    self.button_trans_color = self.change_color(self.button_trans_color2, self.color2, step)
                    pygame.draw.rect(self.screen, self.button_trans_color, (self.x,self.y,self.width,self.height), 0, self.curve)
                    if self.text != '':
                        self.text_trans_color = self.change_color(self.text_trans_color2, self.text_color2, step)
                        text = self.base_font.render(self.text, 1, self.text_trans_color)
                        self.screen.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

                    # Clicking the Button
                    if click[0] == 1:
                        self.click = True

                    if self.click == True and not click[0]:
                        self.release = True

                    if self.release:
                        """If there is an action it is run"""
                        if action:
                            action()
                        if link:
                            webbrowser.open(link)
                        self.release = False
                        self.click = False
    
                else:
                    self.time = pygame.time.get_ticks()
                    self.hover = False
                    self.click = False
                    self.release = False
                    step = (self.time - self.time2) / (self.animation_time / self.animation_speed)
                    """A darker version of image when the player isn't hovering over"""
                    if not self.stop_start_animation:
                        self.button_trans_color2 = self.change_color(self.button_trans_color, self.color, step)
                        pygame.draw.rect(self.screen, self.button_trans_color2, (self.x,self.y,self.width,self.height),0, self.curve)
                    else:
                        pygame.draw.rect(self.screen, self.color, (self.x,self.y,self.width,self.height),0, self.curve)
                    if self.text != '':
                        """Text is blit here"""
                        if not self.stop_start_animation:
                            self.text_trans_color2 = self.change_color(self.text_trans_color, self.text_color, step)
                            text = self.base_font.render(self.text, 1, self.text_trans_color2)
                        else:
                            text = self.base_font.render(self.text, 1, self.text_color)
                        self.screen.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))           

            else:
                if mode == "draw":
                    self.time2 = pygame.time.get_ticks()
                    step = (self.time2 - self.time) / (self.animation_time / self.animation_speed)
                    """Draws a lighter version of the image"""
                    self.button_trans_color = self.change_color(self.button_trans_color2, self.color2, step)
                    pygame.draw.rect(self.screen, self.button_trans_color, (self.x,self.y,self.width,self.height), 0, self.curve)

                if mode == "undraw":
                    self.time = pygame.time.get_ticks()
                    step = (self.time - self.time2) / (self.animation_time / self.animation_speed)
                    """A darker version of image when the player isn't hovering over"""
                    self.button_trans_color2 = self.change_color(self.button_trans_color, self.color, step)
                    pygame.draw.rect(self.screen, self.button_trans_color2, (self.x,self.y,self.width,self.height),0, self.curve)

        if self.buttonType == "Circle":
            """If it is a circle it will draw it here"""
            if outline:
                """draws an outline"""
                pygame.draw.circle(self.screen, outline, (self.x, self.y),self.radius+2.5,0)
            """Trig for area"""
            differenceInX = mouse[0] - self.x
            differenceInY = mouse[1] - self.y
            difference = ( differenceInX**2 + differenceInY**2 )**0.5
            """Info on the circle"""
            if difference <= self.radius:
                self.hover = True
                self.stop_start_animation = False
                self.time2 = pygame.time.get_ticks()
                step = (self.time2 - self.time) / (self.animation_time / self.animation_speed)
                self.button_trans_color = self.change_color(self.button_trans_color2, self.color2, step)
                """Draws a lighter version of the image"""
                pygame.draw.circle(self.screen, self.button_trans_color, (self.x,self.y),self.radius,0)

                if self.text != '':
                    """Text is blit here"""
                    self.text_trans_color = self.change_color(self.text_trans_color2, self.text_color2, step)
                    text = self.base_font.render(self.text, 1, self.text_trans_color)
                    self.screen.blit(text, (self.x - (text.get_width()/2), self.y - (text.get_height()/2)))
      
                # Clicking the Button
                if click[0] == 1:
                    self.click = True

                if self.click == True and not click[0]:
                    self.release = True

                if self.release:
                    """If there is an action it is run"""
                    if action != None:
                        action()
                    if link != None:
                        webbrowser.open(link)
                    self.release = False
                    self.click = False
            else:
                self.time = pygame.time.get_ticks()
                step = (self.time - self.time2) / (self.animation_time / self.animation_speed)
                self.button_trans_color2 = self.change_color(self.button_trans_color, self.color, step)
                self.hover = False
                self.click = False
                self.release = False
                """A darker version of image when the player isn't hovering over"""
                pygame.draw.circle(self.screen, self.button_trans_color2, (self.x,self.y),self.radius,0)

                if self.text != '':
                    """Text is blit here"""
                    self.text_trans_color2 = self.change_color(self.text_trans_color, self.text_color, step)
                    text = self.base_font.render(self.text, 1, self.text_trans_color2)
                    self.screen.blit(text, (self.x - (text.get_width()/2), self.y - (text.get_height()/2)))
                
        if self.buttonType == "Image":
            if outline:
                """draws an outline"""
                pygame.draw.rect(self.screen, outline, (self.x-3,self.y-3,self.width+6,self.height+6),0,self.curve)

            self.image.draw(self.x,self.y)
            
            if self.x+self.width > mouse[0] > self.x and self.y+self.height > mouse[1] > self.y:
                self.time2 = pygame.time.get_ticks()
                step = (self.time2 - self.time) / (self.animation_time / self.animation_speed)
                self.opacity2 = self.change_opacity(self.opacity1, self.opacityb, step)
                self.image.load_image.set_alpha(self.opacity2)
                self.hover = True
                # Clicking the Button
                if click[0] == 1:
                    self.click = True

                if self.click == True and not click[0]:
                    self.release = True

                if self.release:
                    """If there is an action it is run"""
                    if action != None:
                        action()
                    if link != None:
                        webbrowser.open(link)
                    self.release = False
                    self.click = False
            else:
                self.time = pygame.time.get_ticks()
                self.hover = False
                self.click = False
                self.release = False
                step = (self.time - self.time2) / (self.animation_time / self.animation_speed)
                self.opacity1 = self.change_opacity(self.opacity2, self.opacitya, step)
                self.image.load_image.set_alpha(self.opacity1)
    
    def is_hovered(self):
        return self.hover

    def is_clicking(self):
        return self.click

    def change_color(self, original_color, new_color, step_multiplier=0):
        colors = []
        new_color_list = []
        for rgb1, rgb2 in zip(original_color, new_color):
            difference = rgb2 - rgb1
            colors.append(difference)

        color_step = [difference / self.num_frames for difference in colors]

        for og_color_rgb, new_color_rgb, step in zip(original_color, new_color, color_step):
            if og_color_rgb > new_color_rgb:
                if int(og_color_rgb + step_multiplier*step) < new_color_rgb:
                    new_color_list.append(new_color_rgb)
                else:
                    new_color_list.append(int(og_color_rgb + step_multiplier*step))
            else:
                if int(og_color_rgb + step_multiplier*step) > new_color_rgb:
                    new_color_list.append(new_color_rgb)
                else:
                    new_color_list.append(int(og_color_rgb + step_multiplier*step))

        return tuple(new_color_list)
    
    def change_opacity(self, original_opacity, new_opacity, step_multiplier=0):
        new_opacity_return = None
        difference = new_opacity - original_opacity
        opacity_step = difference / self.num_frames
        if original_opacity > new_opacity:
            if int(original_opacity + opacity_step*step_multiplier) < new_opacity:
                new_opacity_return = new_opacity
            else:
                new_opacity_return = int(original_opacity + opacity_step*step_multiplier)
        else:
            if int(original_opacity + opacity_step*step_multiplier) > new_opacity:
              new_opacity_return = new_opacity
            else:
                new_opacity_return = int(original_opacity + opacity_step*step_multiplier)
                
        return new_opacity_return

