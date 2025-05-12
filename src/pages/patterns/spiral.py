from pages.base_page import BasePage
import math
import time
import numpy as np

class SpiralPattern(BasePage):
    def __init__(self, display_adapter):
        super().__init__(display_adapter)
        self.speed = 2.0  # default speed
        
        self.angle = 0
        self.max_length = 50
        self.thickness = 2
        self.last_update_time = 0
    
    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        current_time = time.time()
        update_interval = 0.2 / self.speed  # Adjust interval based on speed
        
        if current_time - self.last_update_time < update_interval:
            return
            
        self.last_update_time = current_time
        
        self.clear_frame()
        
        center_row = self.height // 2
        center_col = self.width // 2
        
        # increase angle for spiral animation
        self.angle += 0.2 * self.speed  # apply speed factor to angle increment
        
        for t in np.arange(0, 50, 0.1):
            # parametric equation for spiral
            r = t * 2
            angle = t * 2 + self.angle
            
            # convert polar to cartesian coordinates
            x = round(center_col + r * math.cos(angle))
            y = round(center_row + r * math.sin(angle))
            
            # add thickness by including adjacent points
            offsets = [
                (0, 0),   # center point
                (0, 1),   # point above
                (1, 1),   # point below
                (1, 0),   # point right
            ]
            
            # apply each offset to create thickness
            for dx, dy in offsets:
                new_x = x + dx
                new_y = y + dy
                
                # check if the point is within the grid
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    self.set_pixel(new_x, new_y, 1)
            
            # break if we've reached the maximum length
            if r > self.max_length:
                break
    
    def render(self):
        return self.frame