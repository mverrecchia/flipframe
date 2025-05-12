import numpy as np
from abc import ABC, abstractmethod

class BasePage(ABC):
    """Base class for all pages."""
    
    def __init__(self, display_adapter):
        self.display_adapter = display_adapter
        self.width = display_adapter.width
        self.height = display_adapter.height
        self.frame = np.zeros((self.height, self.width), dtype=np.uint8)
    
    def initialize(self):
        pass
    
    @abstractmethod
    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        pass
    
    @abstractmethod
    def render(self):
        return self.frame
    
    def cleanup(self):
        pass
    
    def clear_frame(self):
        self.frame = np.zeros((self.height, self.width), dtype=np.uint8)
    
    def set_pixel(self, x, y, value):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.frame[y, x] = value
    
    def get_pixel(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.frame[y, x]
        return 0
    
    def invert(self):
        self.frame = 1 - self.frame
        
    def handle_secondary_button(self):
        print(f"Secondary button pressed on {self.__class__.__name__}")
    
    def handle_slider_change(self, value):
        print(f"Slider value changed to {value} on {self.__class__.__name__}")
        
    def draw_line(self, x0, y0, x1, y1, value=1):
        # Bresenham's line algorithm
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        
        while True:
            self.set_pixel(x0, y0, value)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                if x0 == x1:
                    break
                err += dy
                x0 += sx
            if e2 <= dx:
                if y0 == y1:
                    break
                err += dx
                y0 += sy
    
    def draw_rectangle(self, x, y, width, height, value=1, fill=False):
        if fill:
            for i in range(x, x + width):
                for j in range(y, y + height):
                    self.set_pixel(i, j, value)
        else:
            for i in range(x, x + width):
                self.set_pixel(i, y, value)
                self.set_pixel(i, y + height - 1, value)
            
            for j in range(y, y + height):
                self.set_pixel(x, j, value)
                self.set_pixel(x + width - 1, j, value)