import time
import threading


class InputEvent:
    PRIMARY = "primary"
    SECONDARY = "secondary"
    VALUE_CHANGE = "value_change"

class InputManager:    
    def __init__(self, use_simulator=False):
        self.use_simulator = use_simulator
        self.callbacks = {
            InputEvent.PRIMARY: [],
            InputEvent.SECONDARY: [],
            InputEvent.VALUE_CHANGE: []
        }
        self.button_manager = None
        self.simulator = None
        self.running = False
        self.slider_value = 50
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0
    
    def initialize_hardware(self):
        if self.use_simulator:
            return
        
        try:
            from core.hardware import ButtonManager, Slider, DistanceSensor
            self.button_manager = ButtonManager()
            
            self.button_manager.register_callback('left', lambda: self._handle_event(InputEvent.PRIMARY))
            self.button_manager.register_callback('right', lambda: self._handle_event(InputEvent.SECONDARY))
            
            # slider thread
            self.slider = Slider()
            self.running = True
            self.slider_thread = threading.Thread(target=self._poll_slider)
            self.slider_thread.daemon = True
            self.slider_thread.start()
        
            self.distance = DistanceSensor()
            self.distance_thread = threading.Thread(target=self._poll_distance)
            self.distance_thread.daemon = True
            self.distance_thread.start()
            
        except ImportError as e:
            print(f"Error initializing hardware inputs: {e}")
    
    def initialize_simulator(self, simulator):
        if not self.use_simulator:
            return
        
        self.simulator = simulator
        
        self.simulator.register_button_callback('left', lambda: self._handle_event(InputEvent.PRIMARY))
        self.simulator.register_button_callback('right', lambda: self._handle_event(InputEvent.SECONDARY))
        self.simulator.register_slider_callback(lambda value: self._handle_slider_value_change(value))
    
    def register_callback(self, event_type, callback):
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def process_gestures(self, gestures):
        if not gestures:
            return
        
        current_time = time.time()
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return
    
    def get_slider_value(self):
        if self.use_simulator and self.simulator:
            return self.simulator.get_slider_value()
        elif hasattr(self, 'slider'):
            return self.slider.get_value()
        else:
            return self.slider_value
    
    def _poll_slider(self):
        last_value = None
        
        while self.running:
            if hasattr(self, 'slider'):
                value = self.slider.get_value()
                
                if value != last_value:
                    self._handle_slider_value_change(value)
                    last_value = value
            
            time.sleep(0.1)

    def _poll_distance(self):
        last_value = None
        
        while self.running:
            if hasattr(self, 'distance'):
                value = self.distance.get_value()
                
                if value != last_value:
                    self._handle_distance_value_change(value)
                    last_value = value
            
            time.sleep(0.1)
    
    def _handle_event(self, event_type):
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                callback()
    
    def _handle_slider_value_change(self, value):
        self.slider_value = value
        
        for callback in self.callbacks[InputEvent.VALUE_CHANGE]:
            try:
                callback(value)
            except TypeError:
                callback()
    
    def _handle_distance_value_change(self, value):
        self.distance_value = value
        
        for callback in self.callbacks[InputEvent.VALUE_CHANGE]:
            try:
                callback(value)
            except TypeError:
                callback()

    def cleanup(self):
        self.running = False
        
        if hasattr(self, 'slider_thread') and self.slider_thread.is_alive():
            self.slider_thread.join(timeout=1.0)

        if hasattr(self, 'distance_thread') and self.distance_thread.is_alive():
            self.distance_thread.join(timeout=1.0)
        
        if self.button_manager:
            self.button_manager.cleanup()