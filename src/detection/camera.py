import cv2
import numpy as np
import mediapipe as mp

capture = None
picam2 = None
mp_face_mesh = None
mp_drawing = None
face_mesh = None

IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240

def init(use_simulator=False):
    global capture, picam2, mp_face_mesh, mp_drawing, face_mesh
    
    if use_simulator:
        capture = cv2.VideoCapture(0)
        if not capture.isOpened():
            print("Error: Could not open webcam")
            return False
            
        # Set resolution
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
    else:
        # hardware
        from picamera2 import Picamera2
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()

    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    return True


def get_frame(debug=False):
    # use webcam for simulator
    if capture is not None and capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            print("Error: Failed to capture frame from webcam")
            return None
            
        if frame.shape[1] != IMAGE_WIDTH or frame.shape[0] != IMAGE_HEIGHT:
            frame = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))
            
    # use picamera2/hardware
    elif picam2 is not None:
        try:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            if frame.shape[1] != IMAGE_WIDTH or frame.shape[0] != IMAGE_HEIGHT:
                frame = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))
        except Exception as e:
            print(f"Error capturing frame with picamera2: {e}")
            return None
    else:
        print("No camera available")
        return None
    
    return frame


def get_face_landmarks(frame):
    if face_mesh is None:
        return None
    
    # mediapipe requires rgb
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    rgb_frame.flags.writeable = False
    results = face_mesh.process(rgb_frame)
    rgb_frame.flags.writeable = True
    
    if not results.multi_face_landmarks:
        return None
    
    # convert the first face's landmarks to a numpy array
    face_landmarks = results.multi_face_landmarks[0]
    landmarks_array = np.zeros((468, 2), dtype=np.float32)
    
    image_height, image_width = frame.shape[:2]
    
    for idx, landmark in enumerate(face_landmarks.landmark):
        if idx < 468:
            # convert normalized coordinates to pixel coordinates
            landmarks_array[idx] = [
                landmark.x * image_width,
                landmark.y * image_height
            ]
    
    return landmarks_array

def cleanup():
    global capture, picam2, face_mesh
    
    if capture is not None and capture.isOpened():
        capture.release()
    
    if picam2 is not None:
        picam2.stop()
    
    cv2.destroyAllWindows()
    
    if face_mesh is not None:
        face_mesh.close()