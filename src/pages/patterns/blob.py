from pages.base_page import BasePage
import numpy as np
import random
import math
import time

class BlobPattern(BasePage):
    def __init__(self, display_adapter):
        super().__init__(display_adapter)
        self.speed = 1.0
        self.last_update_time = 0
        
        # Initialize organism state
        self.organism = {
            'x': self.width / 2,
            'y': self.height / 2,
            'radius': 2,
            'maxRadius': 5,
            'growthAccumulator': 0,
            'food': set(),     # store food positions as "x,y" strings
            'consumed': set()  # store consumed food positions
        }
        
        # add initial food dots
        for _ in range(5):
            self.add_new_food_dot()

    def add_new_food_dot(self):
        """Add a new food dot at a random position"""
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            food_key = f"{x},{y}"
            
            # Check if position is already occupied
            if food_key not in self.organism['food']:
                self.organism['food'].add(food_key)
                break

    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        current_time = time.time()
        update_interval = 0.05 / self.speed  # Update every 0.05 seconds
        
        if current_time - self.last_update_time < update_interval:
            return
            
        self.last_update_time = current_time
        
        # Find nearest unconsumed food
        nearest_food = None
        min_distance = float('inf')
        
        for food_pos in self.organism['food']:
            if food_pos not in self.organism['consumed']:
                food_x, food_y = map(float, food_pos.split(','))
                dx = food_x - self.organism['x']
                dy = food_y - self.organism['y']
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_food = (food_x, food_y)
        
        # Move towards nearest food
        if nearest_food:
            base_speed = 0.15
            move_speed = base_speed * (1 - (self.organism['radius'] / self.organism['maxRadius']) * 0.5)
            
            dx = nearest_food[0] - self.organism['x']
            dy = nearest_food[1] - self.organism['y']
            angle = math.atan2(dy, dx)
            
            self.organism['x'] += math.cos(angle) * move_speed
            self.organism['y'] += math.sin(angle) * move_speed
            
            # Check if close enough to consume food
            consume_distance = self.organism['radius']
            if min_distance < consume_distance:
                food_key = f"{int(nearest_food[0])},{int(nearest_food[1])}"
                if food_key not in self.organism['consumed']:
                    self.organism['consumed'].add(food_key)
                    
                    # Growth logic
                    self.organism['growthAccumulator'] += 0.1
                    if self.organism['growthAccumulator'] >= 1:
                        self.organism['radius'] = min(
                            self.organism['maxRadius'],
                            self.organism['radius'] + 0.2
                        )
                        self.organism['growthAccumulator'] = 0
                    
                    # add new food dot
                    self.add_new_food_dot()
        
        # clear the frame
        self.clear_frame()
        
        # draw organism and food
        for y in range(self.height):
            for x in range(self.width):
                # draw unconsumed food dots
                food_key = f"{x},{y}"
                if (food_key in self.organism['food'] and 
                    food_key not in self.organism['consumed']):
                    self.set_pixel(x, y, 1)
                    continue
                
                # draw the organism
                dx = x - self.organism['x']
                dy = y - self.organism['y']
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < self.organism['radius']:
                    sphere_factor = math.cos((distance / self.organism['radius']) * math.pi * 0.5)
                    shading_threshold = 0.7 + (sphere_factor * 0.3)
                    
                    if random.random() < shading_threshold:
                        self.set_pixel(x, y, 1)

    def render(self):
        return self.frame