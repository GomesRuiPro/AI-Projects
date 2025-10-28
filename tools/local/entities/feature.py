from enum import Enum
from typing import List

class FEATURE(Enum):
    
    def __init__(self, description, keywords):
        super().__init__()
        self.description = description
        self.keywords = keywords

class GENERIC(FEATURE):
    GAMEPLAY = ("gameplay", [])
    GRAPHICS = ("graphics", [])
    SOUND = ("sound", [])
    UI = ("ui", [])
    TECHNICAL = ("technical", [])
    SOCIAL = ("social", [])
    MONETIZATION = ("monetization", [])
    STORY = ("story", [])
    # INNOVATION = ("innovation", [])
    # OTHER = ("other", [])
