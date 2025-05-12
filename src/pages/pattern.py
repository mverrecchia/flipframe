from pages.base_page import BasePage
from pages.patterns import PATTERNS

class PatternPage(BasePage):
    def __init__(self, display_adapter):
        super().__init__(display_adapter)
        
        self.patterns = PATTERNS
        
        self.pattern_classes = {key: value[0] for key, value in self.patterns.items()}
        
        self.pattern_keys = list(self.patterns.keys())
        
        self.current_pattern_index = 0
        self.current_pattern_key = self.pattern_keys[self.current_pattern_index]
        self.current_pattern = self.pattern_classes[self.current_pattern_key](display_adapter)
        
        self.pattern_speed = 2.0
        self.min_speed = 0.5
        self.max_speed = 5.0
        if hasattr(self.current_pattern, 'speed'):
            self.current_pattern.speed = self.pattern_speed
            
        self.last_slider_value = None

    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        self.current_pattern.update(camera_frame, face_landmarks, gestures)
    
    def render(self):
        return self.current_pattern.render()
    
    def handle_secondary_button(self):
        self.next_pattern()
    
    def handle_slider_change(self, slider_value):
        if self.last_slider_value is None or abs(slider_value - self.last_slider_value) >= 2:
            self.last_slider_value = slider_value
            
            speed = self.min_speed + (slider_value / 100.0) * (self.max_speed - self.min_speed)
            
            self.set_speed(speed)
    
    def next_pattern(self):
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.pattern_keys)
        new_key = self.pattern_keys[self.current_pattern_index]
        self.set_pattern(new_key)

    def set_pattern(self, pattern_key):
        if pattern_key in self.pattern_classes:
            if hasattr(self.current_pattern, 'cleanup'):
                self.current_pattern.cleanup()
            
            self.current_pattern_key = pattern_key
            self.current_pattern = self.pattern_classes[pattern_key](self.display_adapter)
            
            if hasattr(self.current_pattern, 'initialize'):
                self.current_pattern.initialize()
            
            if hasattr(self.current_pattern, 'speed'):
                self.current_pattern.speed = self.pattern_speed
                
            return True
        return False

    def set_pattern_by_id(self, pattern_id):
        pattern_map = {
            1: "clock",
            2: "spiral", 
            3: "waves",
            4: "blob",
            5: "cascade",
            6: "bounce"
        }
        
        if pattern_id in pattern_map:
            return self.set_pattern(pattern_map[pattern_id])
        return False

    def set_speed(self, speed):
        self.pattern_speed = float(speed)
        if hasattr(self.current_pattern, 'speed'):
            self.current_pattern.speed = self.pattern_speed