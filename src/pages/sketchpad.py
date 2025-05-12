import time
import json
import os
import numpy as np
import requests
import random
import string
from pages.base_page import BasePage
from pages.qr import QRCodePage

MODE_QR = "qr"                  # Displaying QR code for authentication
MODE_DRAWING_QR = "draw_qr"     # Displaying the user's drawing
MODE_DRAWING_MQTT = "draw_mqtt" # Displaying the user's drawing

class SketchpadPage(BasePage):
    def __init__(self, display_adapter):
        super().__init__(display_adapter)
        self.mode = MODE_QR
        self.qr_page = QRCodePage(display_adapter)
        self.drawing = None
        self.last_drawing_time = 0
        self.token = None
        self.drawing_timeout = 300  # show drawing for 5 minutes before returning to QR
        self.token_folder = "tokens"
        self.drawing_folder = "drawings"
        
        os.makedirs(self.token_folder, exist_ok=True)
        os.makedirs(self.drawing_folder, exist_ok=True)
    
    def initialize(self):
        self.clear_frame()
        
        self.token = self._generate_token()
        self._save_token(self.token)
        print(f"SketchpadPage generated token: {self.token}")
        
        self.qr_page.url = "https://chaelchia.com/flip/draw"
        self.qr_page.token = self.token
        self.qr_page.initialize()
        
        self.mode = MODE_QR
        self._check_for_new_drawing()
    
    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        current_time = time.time()
        
        if self.mode == MODE_QR:
            self.qr_page.update(camera_frame, face_landmarks, gestures)
            
            # check for new drawings from qr code
            if self._check_for_new_drawing():
                self.mode = MODE_DRAWING_QR
                self.last_drawing_time = current_time
        
        elif self.mode == MODE_DRAWING_QR:
            # check if drawing timeout has expired
            if current_time - self.last_drawing_time >= self.drawing_timeout:
                # if so, back to QR code mode
                self.token = self._generate_token()
                self._save_token(self.token)
                print(f"SketchpadPage generated new token after timeout: {self.token}")
                
                # update the QR code with new token
                self.qr_page.token = self.token
                self.qr_page.initialize()
                self.mode = MODE_QR
            
            self._check_for_new_drawing()
    
    def render(self):
        if self.mode == MODE_QR:
            return self.qr_page.render()
        elif self.mode == MODE_DRAWING_QR:
            return self.frame
        elif self.mode == MODE_DRAWING_MQTT:
            return self.frame
        return self.frame
    
    def _generate_token(self, length=6):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))

    def _save_token(self, token):
        token_data = {
            "token": token,
            "created": time.time(),
            "expires": time.time() + 3600,  # Token valid for 1 hour
            "used": False
        }
        
        token_file = os.path.join(self.token_folder, f"{token}.json")
        try:
            with open(token_file, 'w') as f:
                json.dump(token_data, f)
        except Exception as e:
            print(f"Error saving token: {e}")
    
    def _check_for_new_drawing(self) -> bool:
        try:            
            response = requests.get(f"http://localhost:5000/api/current_drawing/{self.token}")
            
            if response.status_code == 200:
                drawing_data = response.json()
                
                if 'matrix' in drawing_data:
                    drawing_matrix = np.array(drawing_data['matrix'], dtype=np.uint8)
                    self.frame = drawing_matrix
                    self.last_drawing_time = time.time()
                    self.mode = MODE_DRAWING_QR
                    return True
            
        except Exception as e:
            print(f"Error checking for drawings: {e}")
            return False
    
    def set_drawing(self, data):
        try:
            drawing_matrix = np.zeros((28, 28), dtype=np.uint8)
            
            for row_idx, row_data in data.items():
                drawing_matrix[int(row_idx)] = row_data
                
            self.frame = drawing_matrix
            self.last_drawing_time = time.time()
            self.mode = MODE_DRAWING_MQTT
            return True
            
        except Exception as e:
            print(f"Error converting drawing data to matrix: {e}")
            return False