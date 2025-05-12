from .clock import ClockPattern
from .spiral import SpiralPattern
from .waves import WavesPattern
from .blob import BlobPattern
from .cascade import CascadePattern
from .bounce import BouncePattern

PATTERNS = {
    "clock": (ClockPattern, {
        "name": "ClockPattern",
        "description": "Various passive patterns",
        "camera_features": None
    }),
    "spiral": (SpiralPattern, {
        "name": "SpiralPattern",
        "description": "Various passive patterns",
        "camera_features": None
    }),
    "waves": (WavesPattern, {
        "name": "WavesPattern",
        "description": "Various passive patterns",
        "camera_features": None
    }),
    "blob": (BlobPattern, {
        "name": "BlobPattern",
        "description": "Various passive patterns",
        "camera_features": None
    }),
    "cascade": (CascadePattern, {
        "name": "CascadePattern",
        "description": "Various passive patterns",
        "camera_features": None
    }),
    "bounce": (BouncePattern, {
        "name": "BouncePattern",
        "description": "Various passive patterns",
        "camera_features": None
    })
}