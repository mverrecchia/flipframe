import sys
import numpy as np
import pygame
from core.display import Display, FrameGenerator
from utils.constants import SimConstants as SC

class Disc(pygame.sprite.Sprite):    
    def __init__(self, x, y, diameter, color):
        super().__init__()
        self.diameter = diameter
        self.x = x
        self.y = y
        self.image = pygame.Surface([self.diameter, self.diameter])
        self.image.fill(pygame.Color('black'))
        self.rect = pygame.Rect(self.x, self.y, self.diameter, self.diameter)
        self.center = (self.x + self.diameter/2, self.y + self.diameter/2)
        self.color = color
        self.side = SC.DISC_TOP if self.color == pygame.Color('white') else SC.DISC_BOTTOM
        self.draw(x, y, diameter)
    
    def draw(self, x, y, diameter):
        self.diameter = diameter
        self.x = x
        self.y = y
        self.image = pygame.Surface([self.diameter, self.diameter])
        self.image.fill(pygame.Color('black'))
        self.rect = pygame.Rect(self.x, self.y, self.diameter, self.diameter)
        pygame.draw.circle(self.image, pygame.Color('white'), (self.diameter/2, self.diameter/2), self.diameter/2)
        if self.side == SC.DISC_BOTTOM:
            pygame.draw.circle(self.image, pygame.Color('black'), (self.diameter/2, self.diameter/2), ((1-SC.DISC_BORDER) * self.diameter)/2)
    
    def flip(self, side_req):
        if side_req == SC.DISC_BOTTOM and self.side != side_req:
            self.side = SC.DISC_BOTTOM
            pygame.draw.circle(self.image, pygame.Color('black'), (self.diameter/2, self.diameter/2), ((1-SC.DISC_BORDER) * self.diameter)/2)
        if side_req == SC.DISC_TOP and self.side != side_req:
            self.side = SC.DISC_TOP
            self.image.fill(pygame.Color('black'))
            pygame.draw.circle(self.image, pygame.Color('white'), (self.diameter/2, self.diameter/2), self.diameter/2)


class PushButton(pygame.sprite.Sprite):
    def __init__(self, name, x_ratio, y_ratio, width_ratio, height_ratio):
        super().__init__()
        self.name = name
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.pressed = False
        self.rect = None
        self.font = None
        self.text = None
        self.text_rect = None
        self.callbacks = []
    
    def draw(self, screen, screen_width, screen_height):
        x = screen_width * self.x_ratio
        y = screen_height * self.y_ratio
        width = screen_width * self.width_ratio
        height = screen_height * self.height_ratio
        self.rect = pygame.Rect(x, y, width, height)
        
        # draw button background
        color = pygame.Color('white') if self.pressed else pygame.Color('grey50')
        pygame.draw.rect(screen, color, self.rect, border_radius=int(height / 2))
        
        # draw button text
        self.font = pygame.font.SysFont(None, int(0.8 * height))
        self.text = self.font.render(self.name, True, pygame.Color('white'))
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.rect.center
        screen.blit(self.text, self.text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.pressed = True
            return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed:
                self.pressed = False
                if self.rect.collidepoint(event.pos):
                    for callback in self.callbacks:
                        callback()
                return True
        return False
    
    def register_callback(self, callback):
        self.callbacks.append(callback)


class Slider(pygame.sprite.Sprite):    
    def __init__(self, x_ratio, y_ratio, width_ratio, height_ratio):
        super().__init__()
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.pressed = False
        self.pos = 50  # Default to middle position (0-100)
        self.rect = None
        self.button_rect = None
        self.callbacks = []
    
    def draw(self, screen, screen_width, screen_height):
        x = int(screen_width * self.x_ratio)
        y = int(screen_height * self.y_ratio)
        width = int(screen_width * self.width_ratio)
        height = int(screen_height * self.height_ratio)
        self.rect = pygame.Rect(x, y, width, height)
        
        pygame.draw.rect(screen, pygame.Color('grey90'), self.rect, border_radius=int(width/2))
        
        button_y_pos = y + height - (height * self.pos / 100)
        button_diameter = width * 2
        
        button_x = x - (button_diameter - width) / 2  # center button horizontally
        self.button_rect = pygame.Rect(button_x, button_y_pos - button_diameter/2, button_diameter, button_diameter)
        
        button_surface = pygame.Surface([button_diameter, button_diameter])
        button_surface.fill(pygame.Color('black'))
        button_surface.set_colorkey(pygame.Color('black'))  # Make black transparent
        
        pygame.draw.circle(button_surface, pygame.Color('white'), 
                          (button_diameter/2, button_diameter/2), 
                          button_diameter/2)
        
        screen.blit(button_surface, (button_x, button_y_pos - button_diameter/2))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect and self.button_rect.collidepoint(event.pos):
                self.pressed = True
                return True
            elif self.rect.collidepoint(event.pos):
                self.pressed = True
                self._update_position(event.pos[1])
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.pressed:
                self._update_position(event.pos[1])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed:
                self.pressed = False
                return True
        return False
    
    def _update_position(self, y_pos):
        rel_pos = self.rect.y + self.rect.h - y_pos
        self.pos = int(rel_pos / self.rect.h * 100)
        
        self.pos = max(0, min(100, self.pos))
        
        self._notify_callbacks()
    
    def get_value(self):
        return self.pos
    
    def register_callback(self, callback):
        self.callbacks.append(callback)
    
    def _notify_callbacks(self):
        for callback in self.callbacks:
            callback(self.pos)


class FlipSimDisplay(Display):
    def __init__(self, caption="FLIPSIM"):
        super().__init__()
        self.caption = caption
        self.screen = None
        self.clock = None
        self.running = False
        self.frame_builder = FrameGenerator()
        
        # Simulator components
        self.discs = []
        self.button_left = None
        self.button_right = None
        self.slider = None
        self.all_sprites = None
    
    def initialize(self):
        pygame.init()
        pygame.display.set_caption(self.caption)
        
        # set screen size
        self.screen = pygame.display.set_mode((SC.WINDOW_WIDTH_INIT, SC.WINDOW_HEIGHT_INIT), pygame.RESIZABLE)
        self.screen.fill(pygame.Color('black'))
        
        self.clock = pygame.time.Clock()
        self.all_sprites = pygame.sprite.Group()
        
        screen_width, screen_height = self.screen.get_size()
        disc_size = screen_width / SC.WINDOW_TO_DISC_RATIO
        
        # calculate display position
        display_width = self.width * disc_size
        display_height = self.height * disc_size
        display_x = (screen_width - display_width) / 2
        display_y = (screen_height - display_height) / 3  # position in upper third of window
        
        # create discs for each row, then append rows to the list
        self.discs = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                disc = Disc(
                    display_x + x * disc_size,
                    display_y + y * disc_size,
                    disc_size,
                    pygame.Color('black')
                )
                row.append(disc)
                self.all_sprites.add(disc)
            self.discs.append(row)
        
        # button and slider for the simulator
        self.button_left = PushButton(
            name="L",
            x_ratio=0.25,
            y_ratio=0.85,
            width_ratio=0.15,
            height_ratio=0.08
        )
        
        self.button_right = PushButton(
            name="R",
            x_ratio=0.6,
            y_ratio=0.85,
            width_ratio=0.15,
            height_ratio=0.08
        )
        
        self.slider = Slider(
            x_ratio=0.9,
            y_ratio=0.3,
            width_ratio=0.03,
            height_ratio=0.4
        )
        
        self.running = True
        return True
    
    def send_frame(self, frame_matrix):
        if not self.running:
            return
        
        # update disc states based on frame matrix
        for y in range(min(self.height, len(self.discs))):
            for x in range(min(self.width, len(self.discs[y]))):
                side = SC.DISC_TOP if frame_matrix[y, x] > 0 else SC.DISC_BOTTOM
                self.discs[y][x].flip(side)
        
        self._process_events()
        
        self.screen.fill(pygame.Color('black'))
        self.all_sprites.draw(self.screen)
        
        screen_width, screen_height = self.screen.get_size()
        self.button_left.draw(self.screen, screen_width, screen_height)
        self.button_right.draw(self.screen, screen_width, screen_height)
        self.slider.draw(self.screen, screen_width, screen_height)
        
        # this is what updates the screen
        pygame.display.flip()
        
        self.clock.tick(SC.SIM_FPS)
    
    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self._handle_resize(event)
            else:
                # Let UI elements handle the event
                handled = False
                handled |= self.button_left.handle_event(event)
                handled |= self.button_right.handle_event(event)
                handled |= self.slider.handle_event(event)
    
    # TODO: this still doesn't really work 
    def _handle_resize(self, event):
        screen_width = int(event.h * SC.WINDOW_ASPECT_RATIO)
        screen_height = event.h
        
        # enforce the aspect ratio
        if screen_width > event.w:
            screen_width = event.w
            screen_height = int(screen_width / SC.WINDOW_ASPECT_RATIO)
        
        # Enforce the minimum and maximum sizes
        screen_width = min(max(screen_width, SC.WINDOW_WIDTH_MIN), SC.WINDOW_WIDTH_MAX)
        screen_height = min(max(screen_height, SC.WINDOW_HEIGHT_MIN), SC.WINDOW_HEIGHT_MAX)
        
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        
        disc_size = screen_width * SC.WINDOW_TO_DISC_RATIO
        
        display_width = self.width * disc_size
        display_height = self.height * disc_size
        display_x = (screen_width - display_width) / 2
        display_y = (screen_height - display_height) / 3
        
        for y in range(self.height):
            for x in range(self.width):
                if y < len(self.discs) and x < len(self.discs[y]):
                    self.discs[y][x].draw(
                        display_x + x * disc_size,
                        display_y + y * disc_size,
                        disc_size
                    )
    
    def register_button_callback(self, button, callback):
        if button == 'left' and self.button_left:
            self.button_left.register_callback(callback)
        elif button == 'right' and self.button_right:
            self.button_right.register_callback(callback)
    
    def register_slider_callback(self, callback):
        if self.slider:
            self.slider.register_callback(callback)
    
    def get_slider_value(self):
        return self.slider.get_value() if self.slider else 50
    
    def cleanup(self):
        if pygame.get_init():
            pygame.quit()