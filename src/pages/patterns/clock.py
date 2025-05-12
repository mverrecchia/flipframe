import time
import platform
import os
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pages.base_page import BasePage

class ClockPattern(BasePage):
    def __init__(self, display_adapter):
        super().__init__(display_adapter)
        self.speed = 1.0  # update every second
        self.last_update_time = 0
        self.font_size = 15
        self.matrix_size = 11

        if platform.system() == 'Linux' and os.path.exists('/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf'):
            self.font_name = '/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf'
        else:
            self.font_name = 'Arial Bold'  # this will work on macOS

    def convert_char_to_bitmap(self, char: str) -> np.matrix:
        matrix = np.zeros((self.matrix_size, self.matrix_size), dtype=np.uint8)

        try:
            font = ImageFont.truetype(self.font_name, self.font_size)
        except:
            font = ImageFont.load_default()
            
        image = Image.new('L', (self.font_size, self.font_size), color=0)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), char, font=font, fill=255)
        
        img_array = np.array(image)
        threshold = 127
        binary_array = np.where(img_array > threshold, 1, 0)

        matrix[:,2:9] = binary_array[3:14, 1:8]
        return matrix

    def generate_clock_matrix(self) -> np.array:
        matrix = np.zeros((self.height, self.width), dtype=np.uint8)
        sub_matrices = []
        
        now = datetime.now()
        time_str = now.strftime("%H%M")
        
        for char in time_str:
            sub_matrices.append(self.convert_char_to_bitmap(char))

        matrix[2:13, 3:14] = sub_matrices[0]   # Hours tens
        matrix[2:13, 14:25] = sub_matrices[1]  # Hours ones
        matrix[15:26, 3:14] = sub_matrices[2]  # Minutes tens
        matrix[15:26, 14:25] = sub_matrices[3] # Minutes ones
        
        return matrix

    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        current_time = time.time()
        update_interval = 1.0 / self.speed  # Update every second
        
        if current_time - self.last_update_time < update_interval:
            return
            
        self.last_update_time = current_time
        
        self.clear_frame()
        clock_matrix = self.generate_clock_matrix()
        
        for y in range(self.height):
            for x in range(self.width):
                self.set_pixel(x, y, clock_matrix[y, x])

    def render(self):
        return self.frame
        
    def handle_slider_change(self, value):
        print("speed not used by clock")