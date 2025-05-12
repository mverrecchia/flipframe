from pages.base_page import BasePage
import numpy as np
import random
import math
import time

class BouncePattern(BasePage):
    def __init__(self, display_adapter):
        super().__init__(display_adapter)
        self.speed = 1.0
        self.last_update_time = 0
        
        # initialize ball state
        self.ball = {
            'x': self.width / 2,  # start in middle
            'y': self.height / 2,
            'dx': 0.2,  # initial velocity
            'dy': 0.2
        }
        
        # normalize initial velocity
        speed = math.sqrt(self.ball['dx']**2 + self.ball['dy']**2)
        self.ball['dx'] /= speed
        self.ball['dy'] /= speed

    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        current_time = time.time()
        update_interval = 0.05 / self.speed  # update every 0.05 seconds
        
        if current_time - self.last_update_time < update_interval:
            return
            
        self.last_update_time = current_time
        
        self.ball['x'] += self.ball['dx']
        self.ball['y'] += self.ball['dy']
        
        if self.ball['x'] <= 0 or self.ball['x'] >= self.width - 2:
            self.ball['dx'] *= -1
            self.ball['x'] = max(0, min(self.width - 2, self.ball['x']))
            self.ball['x'] = max(0, min(self.width - 2, self.ball['x']))
            
            self.ball['dy'] += (random.random()) * 0.3
            speed = math.sqrt(self.ball['dx']**2 + self.ball['dy']**2)
            self.ball['dx'] /= speed
            self.ball['dy'] /= speed
        
        if self.ball['y'] <= 0 or self.ball['y'] >= self.height - 2:
            self.ball['dy'] *= -1
            self.ball['y'] = max(0, min(self.height - 2, self.ball['y']))
            
            self.ball['dx'] += (random.random()) * 0.3
            speed = math.sqrt(self.ball['dx']**2 + self.ball['dy']**2)
            self.ball['dx'] /= speed
            self.ball['dy'] /= speed
        
        # clear the frame
        self.clear_frame()
        
        # draw 2x2 ball
        ball_x = int(self.ball['x'])
        ball_y = int(self.ball['y'])
        
        for dy in range(2):
            for dx in range(2):
                x = ball_x + dx
                y = ball_y + dy
                
                # check bounds (shouldn't be necessary now but kept for safety)
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.set_pixel(x, y, 1)

    def render(self):
        return self.frame