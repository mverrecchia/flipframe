import numpy as np
import time
from pages.base_page import BasePage

class EmojiPage(BasePage):    
    def __init__(self, display_adapter):
        super().__init__(display_adapter)
        
        self.face_height = 22  # top 22 rows for face
        
        self.last_update_time = 0
        self.update_interval = 0.1  # 10 FPS
        self.default_face = self._create_default_face()
        self.no_face_counter = 0
        self.max_no_face_count = 30
        
        self.last_face_bounds = None
        self.scaling_factors = None
        
        # FPS tracking debug
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
    
    def initialize(self):
        self.clear_frame()
        self.frame = self.default_face.copy()
        self.start_time = time.time()
        self.frame_count = 0
    
    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        current_time = time.time()
        
        self.frame_count += 1
        elapsed = current_time - self.start_time
        if elapsed >= 5:  # Print every 5 seconds
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = current_time
        
        if current_time - self.last_update_time < self.update_interval:
            return
        
        self.last_update_time = current_time
        
        has_face_data = face_landmarks is not None and len(face_landmarks) > 0
        
        if has_face_data or gestures:
            self.no_face_counter = 0
            
            self._process_landmarks_and_gestures(face_landmarks if has_face_data else None, gestures)
        else:
            self.no_face_counter += 1
            
            if self.no_face_counter >= self.max_no_face_count:
                self.frame = self.default_face.copy()
    
    def render(self):
        return self.frame
    
    def _create_default_face(self):
        face = np.zeros((self.face_height, self.width), dtype=np.uint8)
        
        # draw eyes (simple squares)
        for i in range(3):
            for j in range(3):
                face[10 + i, 8 + j] = 1  # left eye
                face[10 + i, 17 + j] = 1  # Right eye
        
        # draw eyebrows (simple lines)
        for i in range(5):
            face[6, 6 + i] = 1  # left eyebrow
            face[6, 17 + i] = 1  # right eyebrow
                
        # create full frame with empty text area
        full_frame = np.zeros((self.height, self.width), dtype=np.uint8)
        full_frame[:self.face_height, :] = face
        
        return full_frame
    
    def _process_landmarks_and_gestures(self, face_landmarks, gestures):
        # clear just the face portion of the frame
        self.frame[:self.face_height, :] = 0
        
        if face_landmarks is not None and len(face_landmarks) > 0:
            # get face dimensions (assuming normalized coordinates)
            x_coords = face_landmarks[:, 0]
            y_coords = face_landmarks[:, 1]
            
            # simple face bounding box
            x_min, x_max = np.min(x_coords), np.max(x_coords)
            y_min, y_max = np.min(y_coords), np.max(y_coords)
            w, h = x_max - x_min, y_max - y_min
            
            # performance optimization: only recalculate scaling if face bounds changed significantly
            if (self.last_face_bounds is None or 
                    abs(x_min - self.last_face_bounds[0]) > 5 or 
                    abs(y_min - self.last_face_bounds[1]) > 5 or
                    abs(w - self.last_face_bounds[2]) > 5 or
                    abs(h - self.last_face_bounds[3]) > 5):
                
                # scale factor to map face coordinates to display
                scale_x = self.width / w if w > 0 else 1
                scale_y = self.height / h if h > 0 else 1
                
                self.scaling_factors = (scale_x, scale_y, x_min, y_min)
                self.last_face_bounds = (x_min, y_min, w, h)

            # use cached scaling factors
            scale_x, scale_y, bx_min, by_min = self.scaling_factors

            # continue with the rest of the face landmark processing
            # eyebrows
            left_eyebrow_indices = [336, 296, 334, 293, 300]
            right_eyebrow_indices = [70, 63, 105, 66, 107]
            # left eye 
            left_eye_indices = [362, 374, 386, 263, 466]
            # right eye
            right_eye_indices = [33, 145, 159, 133, 173]
            # mouth
            outer_mouth_indices = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]

            # faster mapping function using the cached scaling
            def map_to_display(x, y):
                display_x = int((x - bx_min) * scale_x)
                display_y = int((y - by_min) * scale_y)
                return min(max(0, display_x), self.width - 1), min(max(0, display_y), self.height - 1)

            # draw left eyebrow
            prev_points = {}  # Cache for previously calculated points
            
            # draw left eyebrow with increased distance from eye - only use the arc of top points
            prev_point = None
            # sort left eyebrow points by x-coordinate to ensure we draw from left to right
            left_eyebrow_points = []
            for idx in left_eyebrow_indices:
                if idx < len(face_landmarks):
                    point = (face_landmarks[idx, 0], face_landmarks[idx, 1] - 0.015, idx)
                    left_eyebrow_points.append(point)
            
            left_eyebrow_points.sort()  # Sort by x-coordinate
            
            for x_original, y_adjusted, idx in left_eyebrow_points:
                # Map to display coordinates
                point_key = f"{x_original:.2f}_{y_adjusted:.2f}"
                if point_key in prev_points:
                    x, y = prev_points[point_key]
                else:
                    x, y = map_to_display(x_original, y_adjusted)
                    prev_points[point_key] = (x, y)
                    
                self.set_pixel(x, y, 1)
                
                if prev_point is not None:
                    # Draw line to connect points
                    self.draw_line(prev_point[0], prev_point[1], x, y)
                
                prev_point = (x, y)
            
            # draw right eyebrow
            prev_point = None
            # sort right eyebrow points by x-coordinate
            right_eyebrow_points = []
            for idx in right_eyebrow_indices:
                if idx < len(face_landmarks):
                    point = (face_landmarks[idx, 0], face_landmarks[idx, 1] - 0.015, idx)
                    right_eyebrow_points.append(point)
            
            right_eyebrow_points.sort()
            
            for x_original, y_adjusted, idx in right_eyebrow_points:
                # Map to display coordinates
                point_key = f"{x_original:.2f}_{y_adjusted:.2f}"
                if point_key in prev_points:
                    x, y = prev_points[point_key]
                else:
                    x, y = map_to_display(x_original, y_adjusted)
                    prev_points[point_key] = (x, y)
                    
                self.set_pixel(x, y, 1)
                
                if prev_point is not None:
                    # Draw line to connect points
                    self.draw_line(prev_point[0], prev_point[1], x, y)
                
                prev_point = (x, y)

            # Use the top and bottom points from our reduced set
            left_eye_top_idx = 386  # Top central point
            left_eye_bottom_idx = 374  # Bottom central point
            
            right_eye_top_idx = 159  # Top central point
            right_eye_bottom_idx = 145  # Bottom central point
            
            if (left_eye_top_idx < len(face_landmarks) and left_eye_bottom_idx < len(face_landmarks) and
                    right_eye_top_idx < len(face_landmarks) and right_eye_bottom_idx < len(face_landmarks)):
                # calculate eye openness as distance between top and bottom points
                if h > 0:  # prevent division by zero
                    left_openness = (face_landmarks[left_eye_bottom_idx, 1] - face_landmarks[left_eye_top_idx, 1]) / h
                    right_openness = (face_landmarks[right_eye_bottom_idx, 1] - face_landmarks[right_eye_top_idx, 1]) / h
                    
                    left_eye_size = max(1, min(3, int(left_openness * 50)))  # Reduced from 150 to 50
                    right_eye_size = max(1, min(3, int(right_openness * 50)))  # Reduced from 150 to 50
                
            # get eye centers from the central eye points
            if all(idx < len(face_landmarks) for idx in left_eye_indices + right_eye_indices):
                left_eye_x = np.mean([face_landmarks[idx, 0] for idx in left_eye_indices])
                left_eye_y = np.mean([face_landmarks[idx, 1] for idx in left_eye_indices])
                
                right_eye_x = np.mean([face_landmarks[idx, 0] for idx in right_eye_indices])
                right_eye_y = np.mean([face_landmarks[idx, 1] for idx in right_eye_indices])
                
                # Draw left eye (square) - Position lower below eyebrows
                center_x, center_y = map_to_display(left_eye_x, left_eye_y + 0.02)  # Move down by adjusting y coordinate
                half_size = left_eye_size // 2
                
                # Draw a square centered at the eye position - use rectangle for efficiency
                self.draw_rectangle(
                    center_x - half_size, 
                    center_y - half_size, 
                    half_size * 2 + 1, 
                    half_size * 2 + 1, 
                    value=1, 
                    fill=True
                )
                
                # draw right eye (square) - Position lower below eyebrows
                center_x, center_y = map_to_display(right_eye_x, right_eye_y + 0.02)  # Move down by adjusting y coordinate
                half_size = right_eye_size // 2
                
                # draw a square centered at the eye position - use rectangle for efficiency
                self.draw_rectangle(
                    center_x - half_size, 
                    center_y - half_size, 
                    half_size * 2 + 1, 
                    half_size * 2 + 1, 
                    value=1, 
                    fill=True
                )
            
            # draw mouth outline - if we have enough points
            valid_mouth_points = [idx for idx in outer_mouth_indices if idx < len(face_landmarks)]
            if len(valid_mouth_points) >= 2:
                mouth_points = face_landmarks[valid_mouth_points]
                mouth_center_x = np.mean(mouth_points[:, 0])
                mouth_center_y = np.mean(mouth_points[:, 1])
                
                # find mouth corners - simplify by taking first and middle points if available
                if len(valid_mouth_points) >= 10:
                    left_corner_idx = 0
                    right_corner_idx = len(valid_mouth_points) // 2
                    
                    left_corner = mouth_points[left_corner_idx]
                    right_corner = mouth_points[right_corner_idx]
                    
                    # draw the mouth based on gesture detection
                    center_x, center_y = map_to_display(mouth_center_x, mouth_center_y)
                    # make sure mouth stays within face area
                    center_y = min(center_y, self.face_height - 2)
                    mouth_width = int(abs(map_to_display(left_corner[0], 0)[0] - map_to_display(right_corner[0], 0)[0]) * 0.8)
                    
                    mouth_width = max(4, mouth_width)
                    show_smile = False
                    
                    if gestures.get('open_palm', 0) > 0.7:
                        show_smile = True
                        
                    # draw mouth - smile if palm detected, straight line otherwise
                    if show_smile:
                        # draw a curved up line (smile)
                        curve_amount = 2  # Pixels to curve up/down at the ends
                        for i in range(-mouth_width // 2, mouth_width // 2 + 1):
                            x = center_x + i
                            # Parabolic curve: y = ax²
                            if mouth_width > 0:
                                curve = int(curve_amount * (i / (mouth_width / 2)) ** 2)
                                y = center_y - curve  # Curve upward for smile
                                if 0 <= x < self.width and 0 <= y < self.face_height:  # Ensure within face area
                                    self.set_pixel(x, y, 1)
                    else:
                        # draw a straight line for neutral expression - use line drawing for efficiency
                        self.draw_line(
                            center_x - mouth_width // 2,
                            center_y,
                            center_x + mouth_width // 2,
                            center_y
                        )
        
        # process gestures if available (this part can run even if face_landmarks is None)
        if gestures:
            show_smile = False
            
            if gestures.get('open_palm', 0) > 0.7:
                show_smile = True
                
            if face_landmarks is not None and len(face_landmarks) > 0:
                pass