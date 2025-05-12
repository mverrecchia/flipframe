from pages.base_page import BasePage
import math
import time

class WavesPattern(BasePage):
    def __init__(self, display_adapter):
        super().__init__(display_adapter)
        self.speed = 2.0  # Default speed
        
        self.phase = 0
        self.amplitude = self.height / 6
        self.last_update_time = 0
    
    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        current_time = time.time()
        update_interval = 0.2 / self.speed
        
        if current_time - self.last_update_time < update_interval:
            return
            
        self.last_update_time = current_time
        
        self.clear_frame()
        self.phase += 0.2 * self.speed
        
        for col in range(self.width):
            # calculate wave height for this column
            wave1 = math.sin(self.phase + (col * 0.3)) * self.amplitude
            wave2 = math.sin((self.phase * 0.7) + (col * 0.4)) * (self.amplitude * 0.5)
            wave_height = wave1 + wave2
            
            center_row = self.height // 2
            wave_row = round(center_row + wave_height)
            
            # draw the wave with some thickness
            for thickness in range(-1, 2):
                row = wave_row + thickness
                
                if 0 <= row < self.height:
                    self.set_pixel(col, row, 1)
    
    def render(self):
        return self.frame

    def handle_slider_change(self, value):
        min_speed = 0.5
        max_speed = 2.0
        speed = min_speed + (value / 100.0) * (max_speed - min_speed)
        self.speed = speed
        print(f"Updated waves pattern speed to {speed:.2f} (slider: {value}%)") 