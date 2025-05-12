from pages.base_page import BasePage
import time
import numpy as np

class CascadePattern(BasePage):
    def __init__(self, display_adapter):
        super().__init__(display_adapter)
        self.speed = 0.5  # Default speed
        
        # pattern-specific state
        self.direction = True  # True = going to white, False = going to black
        self.flipped_discs = []  # currently flipping discs
        self.all_discs = set()   # all white discs
        self.total_flipped = 0
        self.max_flips = min(self.width, self.height) * 50
        self.current_interval = 1000
        self.base_min_interval = 100  # base minimum interval
        self.min_interval = self.base_min_interval
        self.last_flip_time = 0
        self.is_active = True
        self.last_update_time = 0
        
        # initialize intervals based on starting speed
        self._update_intervals()
        
    def _update_intervals(self):
        """Update both current and minimum intervals based on speed"""
        self.min_interval = self.base_min_interval / self.speed
        self.current_interval = max(self.min_interval, self.current_interval)

    def handle_slider_change(self, value):
        """Optional: Handle slider changes directly"""
        self.speed = value
        self._update_intervals()

    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        self.clear_frame()
        
        speed_factor = self.speed
        current_time = time.time() * 1000
        
        if current_time - self.last_flip_time > self.current_interval:
            flips_per_update = max(1, self.total_flipped // 20)
            
            for _ in range(flips_per_update):
                available_positions = []
                
                for row in range(self.height):
                    for col in range(self.width):
                        index = row * self.width + col
                        if (self.direction and index not in self.all_discs) or \
                           (not self.direction and index in self.all_discs and index not in self.flipped_discs):
                            available_positions.append(index)
                
                # if there are positions available, flip one
                if available_positions:
                    random_index = np.random.randint(0, len(available_positions))
                    disc_index = available_positions[random_index]
                    
                    # add to flipped discs
                    self.flipped_discs.append(disc_index)
                    
                    # Update all_discs based on direction
                    if self.direction:
                        self.all_discs.add(disc_index)  # add when going to white
                    else:
                        self.all_discs.remove(disc_index)  # remove when going to black
                    
                    self.total_flipped += 1
                else:
                    # reset pattern when all discs are flipped
                    self.direction = not self.direction
                    self.flipped_discs = []
                    self.total_flipped = 0
                    self.current_interval = self.min_interval  # reset speed
                    break
            
            self.last_flip_time = current_time
            
            progress_factor = self.total_flipped / self.max_flips
            base_acceleration = 0.99 - progress_factor
            acceleration_factor = min(0.9, base_acceleration * (1 + self.speed * 2))
            
            adjusted_min_interval = self.min_interval / speed_factor
            
            self.current_interval = max(
                adjusted_min_interval,
                self.current_interval * acceleration_factor
            )
        
        for index in self.all_discs:
            row = index // self.width
            col = index % self.width
            self.set_pixel(col, row, 1)
            
    def render(self):
        return self.frame