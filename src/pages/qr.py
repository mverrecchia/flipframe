import numpy as np
import time
import json
import os
import qrcode
from pages.base_page import BasePage

class QRCodePage(BasePage):    
    def __init__(self, display_adapter):
        super().__init__(display_adapter)
        self.qr_matrix = None
        self.url = "https://example.com/auth"  # Default URL
        self.token = None
        self.last_update_time = 0
        self.refresh_interval = 60.0  # Refresh token every minute
        self.token_folder = "tokens"  # Add token folder path
        
        # Ensure token folder exists
        os.makedirs(self.token_folder, exist_ok=True)
    
    def initialize(self):
        self.clear_frame()
        self._generate_qr_code()
    
    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        current_time = time.time()
        
        # Refresh QR code periodically
        if current_time - self.last_update_time >= self.refresh_interval:
            self.last_update_time = current_time
            self._generate_qr_code()
    
    def render(self):
        if self.qr_matrix is not None:
            return self.qr_matrix
        else:
            return self.frame
    
    def _generate_qr_code(self):
        try:
            self.last_update_time = time.time()
            
            if self.token is None:
                self.token = self._generate_token()

            base_url = self.url
            if base_url.startswith("https://"):
                base_url = base_url[8:]
            url_with_token = f"{base_url}?t={self.token}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1,
                border=0
            )
            qr.add_data(url_with_token)
            qr.make(fit=True)
            
            # Convert to matrix
            qr_img = qr.make_image(fill_color=1, back_color=0)
            qr_matrix = np.array(qr_img.get_image(), dtype=np.uint8)
            
            # Convert RGB to binary if needed (check if there's a 3rd dimension)
            if len(qr_matrix.shape) == 3:
                # just the first channel since it's binary data
                qr_matrix = qr_matrix[:, :, 0]
            
            # center the 25x25 onto a 27x27
            bordered_matrix = np.zeros((27, 27), dtype=np.uint8)
            bordered_matrix[1:26, 1:26] = qr_matrix

            bordered_matrix[0, :] = 0  # Top border
            bordered_matrix[26, :] = 0  # Bottom border
            bordered_matrix[:, 0] = 0   # Left border
            bordered_matrix[:, 26] = 0  # Right border

            # put the 27x27 into the top left corner of a 28x28
            final_matrix = np.zeros((28, 28), dtype=np.uint8)
            final_matrix[0:27, 0:27] = bordered_matrix

            self.qr_matrix = final_matrix
        except Exception as e:
            print(f"Error generating QR code: {e}")
            import traceback
            traceback.print_exc()

    def _generate_token(self, length=6):
        import random
        import string
        
        # Generate a random token of specified length
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
    