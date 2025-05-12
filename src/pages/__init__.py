# Import pages to register
from pages.emoji import EmojiPage
from pages.sketchpad import SketchpadPage
from pages.pattern import PatternPage

# Page registry with metadata
PAGES = {
    "pattern": (PatternPage, {
        "name": "PatternPage",
        "description": "Digital or analog clock",
        "camera_features": None
    }),
    "emoji": (EmojiPage, {
        "name": "Emoji Face",
        "description": "Face reactions based on camera input",
        "camera_features": ["landmark_detection", "gesture_detection"]
    }),
    "sketchpad": (SketchpadPage, {
        "name": "Sketchpad",
        "description": "Draw from webpage",
        "camera_features": None
    })
}