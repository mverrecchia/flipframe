import cv2
import numpy as np
import mediapipe as mp

mp_hands = None
hands = None

def init():
    global mp_hands, hands
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    return True


def detect_gestures(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame.flags.writeable = False
    results = hands.process(rgb_frame)
    rgb_frame.flags.writeable = True
    
    gestures = {}
    
    if not results.multi_hand_landmarks:
        return gestures
    
    for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
        if results.multi_handedness and hand_idx < len(results.multi_handedness):
            hand_info = results.multi_handedness[hand_idx]
            hand_label = hand_info.classification[0].label
            confidence = hand_info.classification[0].score
        else:
            hand_label = f"Hand_{hand_idx}"
            confidence = 1.0
        
        landmarks = []
        for landmark in hand_landmarks.landmark:
            landmarks.append([landmark.x, landmark.y, landmark.z])
        landmarks = np.array(landmarks)
        
        gesture_name, gesture_confidence = _classify_gesture(landmarks, hand_label)
        
        if gesture_name:
            combined_confidence = confidence * gesture_confidence
            gestures[gesture_name] = combined_confidence
    
    return gestures


def _classify_gesture(landmarks, hand_label):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    wrist = landmarks[0]
    
    thumb_mcp = landmarks[2]
    index_mcp = landmarks[5]
    middle_mcp = landmarks[9]
    ring_mcp = landmarks[13]
    pinky_mcp = landmarks[17]
    
    thumb_extended = thumb_tip[1] < thumb_mcp[1]
    index_extended = index_tip[1] < index_mcp[1]
    middle_extended = middle_tip[1] < middle_mcp[1]
    ring_extended = ring_tip[1] < ring_mcp[1]
    pinky_extended = pinky_tip[1] < pinky_mcp[1]
    
    extended_count = sum([thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended])
    
    if extended_count >= 4:
        return "open_palm", 0.8
    
    # no recognized gesture
    return None, 0.0


def cleanup():
    global hands
    
    if hands is not None:
        hands.close()