from enum import Enum
from pathlib import Path


class BeatType(Enum):
    BEAT = "beat"
    MEASURE = "measure"
    STEP = "step"


class SoundLibrary(Enum):
    NORMAL = "normal"


ASSETS_DIR = Path(__file__).resolve().parent / "assets"
